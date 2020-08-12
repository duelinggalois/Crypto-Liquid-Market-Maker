import abc
import logging.config
import sys
from collections import defaultdict
from decimal import Decimal

from sqlalchemy.exc import OperationalError

import config
from trader.database.db import dal
from trader.exchange.api_enum import ApiEnum
from trader.exchange.api_provider import ApiProvider
from trader.operations.book_manager import book_manager_maker
from trader.database.models.trading_terms import TradingTerms
from trader.socket.trading_threads import (
  InitialSendOrderThread, AdjustOrdersThread, CancelOrdersThread
)

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class AbstractThreadHandler(abc.ABC):

  @abc.abstractmethod
  def add_terms(self, terms: TradingTerms):
    pass

  @abc.abstractmethod
  def remove_terms(self, terms: TradingTerms):
    pass

  @abc.abstractmethod
  def get_threads(self, pair):
    pass

  @abc.abstractmethod
  def check_book_for_match(self, message):
    """Check if matched trade is in book and process trade if it is
    """
    pass

  @abc.abstractmethod
  def handle_last_match_message(self, message):
    pass


class ThreadHandler(AbstractThreadHandler):
  """Class handles the boundary between asynchronous code handling socket input
  and synchronous code to handle messages. Threads are used to isolate
  synchronous code.
  """

  def __init__(self, api_enum=ApiEnum.NoopApi):
    self.trading_api = ApiProvider.get_api(api_enum)
    self.details_for_pairs = {}
    self.book_manager = None
    # threads that will run to completion unless canceled
    self._immutable_threads = defaultdict(list)
    # threads that can be overridden by other threads of the same type
    self._sell_threads = defaultdict(list)
    self._buy_threads = defaultdict(list)
    # mostly for testing
    self._cancel_threads = []
    self.session_errors = 0

    self.get_threads_from_dict = lambda thread_dict: [
      t for t_list in thread_dict.values() for t in t_list
    ]

    self.get_all_immutable_threads = lambda: self.get_threads_from_dict(
      self._immutable_threads
    )

    self.get_all_mutable_threads = lambda: self.get_threads_from_dict(
      self._sell_threads) + self.get_threads_from_dict(self._buy_threads)

    self.get_all_threads_for_pair = lambda pair: self._immutable_threads[
      pair] + self._sell_threads[pair] + self._buy_threads[pair]

  def get_all_threads(self):
    return self.get_threads_from_dict(self._immutable_threads) + \
           self.get_threads_from_dict(self._buy_threads) + \
           self.get_threads_from_dict(self._sell_threads) + \
           self._cancel_threads

  def add_terms(self, terms: TradingTerms,
                BookManagerMaker=None):
    pair = terms.pair
    self.details_for_pairs[pair] = {
      "socket_ready": False,
      "BookManagerMaker": book_manager_maker(
        terms, trading_api=self.trading_api
      ) if BookManagerMaker is None else BookManagerMaker
    }

  def remove_terms(self, terms: TradingTerms):
    self.clean_thread_pools()
    pair = terms.pair
    details = self.details_for_pairs.pop(pair, None)
    BookManagerMaker = details["BookManagerMaker"]
    if BookManagerMaker is None:
      logger.warning("could not find terms to remove: {}".format(terms))
      return

    self.cancel_threads_for_pair(terms.pair)

    thread = CancelOrdersThread(BookManagerMaker())
    self._cancel_threads.append(thread)
    thread.start()

  def get_threads(self, pair):
    return self._sell_threads[pair] + self._buy_threads[pair] + \
           self._immutable_threads[pair]

  def check_book_for_match(self, match):

    pair = match["product_id"]
    try:
      book_manager = self.details_for_pairs[pair]["BookManagerMaker"]()
      book_manager.load_book()
      order = book_manager.look_for_order(match)

      if order is None:
        logger.info("Matched trade not in book")
        return

      logger.info("Matched trade is in book")
      match_size = Decimal(match["size"])

      is_order_filled = book_manager.update_order(order, match_size)

      if is_order_filled:
        logger.info("Match filled order")
        # order was loaded in current thread, passing it as a dictionary
        # to avoid session errors caused by passing it directly
        order_description = {
          "side": order.side,
          "size": order.size,
          "price": order.price
        }
        # Thread will open its own book
        book_manager.close_book()
        self.handle_full_match(pair, order_description)
      else:
        logger.info("Match filled {} of order, {} is remaining."
                    .format(Decimal(match_size), order.size - order.filled))
        book_manager.close_book()

      # Reset error count for successful check of match.
      self.session_errors = 0
    except OperationalError as e:
      dal.connect()
      self.session_errors += 1
      if self.session_errors < 3:
        logger.warning(
          "Attempting to reconnect for database exception: {}".format(e.args)
        )
        self.check_book_for_match(match)
        self.session_errors = 0
      else:
        raise e

  def handle_full_match(self, pair, order_desc):
    if order_desc["side"] == "buy":
      # a buy order triggers listing sells and vise versa
      self.start_sell_thread(pair, order_desc)
    else:
      self.start_buy_thread(pair, order_desc)

  def handle_last_match_message(self, message):
    self.clean_thread_pools()
    pair = message["product_id"]
    socket_status = self.details_for_pairs[pair]["socket_ready"]
    BookManagerMaker = self.details_for_pairs[pair]["BookManagerMaker"]
    logger.debug("handle last match, pair {} socket_ready: {}".format(
      pair, socket_status))
    if not socket_status:
      logger.debug("Sending orders")
      initial_thread = InitialSendOrderThread(BookManagerMaker())

      self.check_immutable_threads(initial_thread)
      self.check_mutable_threads(pair, initial_thread)

      initial_thread.start()
      self._immutable_threads[pair].append(initial_thread)
      self.details_for_pairs[pair]["socket_ready"] = True
    else:
      self.check_book_for_match(message)

  def start_sell_thread(self, pair, order_desc):
    self.clean_thread_pools()
    book_manager = self.details_for_pairs[pair]["BookManagerMaker"]()
    thread = AdjustOrdersThread(book_manager, order_desc)

    self.check_immutable_threads(thread)
    self.check_mutable_threads(pair, thread, sell_priority=order_desc["size"])

    thread.start()
    self._sell_threads[pair].append(thread)

  def start_buy_thread(self, pair, order_desc):

    self.clean_thread_pools()
    book_manager = self.details_for_pairs[pair]["BookManagerMaker"]()
    thread = AdjustOrdersThread(book_manager, order_desc)

    self.check_immutable_threads(thread)
    self.check_mutable_threads(pair, thread, buy_priority=order_desc["size"])

    thread.start()
    self._buy_threads[pair].append(thread)

  def check_immutable_threads(self, thread):

    if len(self.get_all_immutable_threads()) > 0:
      self.pause_immutable_thread(thread)

  def pause_immutable_thread(self, thread):

    for immutable_thread in self.get_all_immutable_threads():
      if immutable_thread.is_alive():
        immutable_thread.intervene(0, thread)

  def check_mutable_threads(self, pair, thread, buy_priority=None,
                            sell_priority=None):

    priority_over_buys = 0 if buy_priority is None else buy_priority
    priority_over_sells = 0 if sell_priority is None else sell_priority

    buy_threads = self._buy_threads[pair]
    sell_threads = self._sell_threads[pair]

    for other_thread in buy_threads:
      other_thread.intervene(priority_over_buys, thread)

    for other_thread in sell_threads:
      other_thread.intervene(priority_over_sells, thread)

    # pause threads for other pairs to avoid maxing out api rate limits
    for other_thread in self.get_all_mutable_threads():
      if other_thread in buy_threads:
        continue
      if other_thread not in sell_threads:
        continue
      other_thread.intervene(0, thread)

  def cancel_threads_for_pair(self, pair):

    for thread in self.get_all_threads_for_pair(pair):
      if thread.is_alive():
        # kill thread, max size will ensure the thread ends
        thread.intervene(sys.maxsize, None)

  def clean_thread_pools(self):

    for key in self._immutable_threads.keys():
      self._immutable_threads[key] = [
        t for t in self._immutable_threads[key] if t.is_alive()
      ]

    for key in self._sell_threads.keys():
      self._sell_threads[key] = [
        t for t in self._sell_threads[key] if t.is_alive()
      ]

    for key in self._buy_threads.keys():
      self._buy_threads[key] = [
        t for t in self._buy_threads[key] if t.is_alive()
      ]

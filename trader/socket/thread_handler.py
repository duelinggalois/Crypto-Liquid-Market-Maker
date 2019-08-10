import logging.config
import queue
import threading
from decimal import Decimal

import config

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class ThreadHandler:
  """Class handles the boundary between asynchronous code handling socket input
  and synchronous code to handle messages. Threads are used to isolate
  synchronous code.
  """

  def __init__(self, book_manager):
    self.book_manager = book_manager
    self.initial_thread = None
    self.initial_done = False
    self._sell_threads = []
    self._buy_threads = []

  def get_threads(self):
    return self._sell_threads + self._buy_threads + [self.initial_thread]

  def check_book_for_match(self, match):
    """Check if matched trade is in book and process trade if it is
    """
    logger.info("Checking book for matched trade")
    self.book_manager.load_book()
    order = self.book_manager.look_for_order(match)

    if order is None:
      logger.info("Matched trade not in book")
      return

    logger.info("Matched trade is in book")
    match_size = Decimal(match["size"])

    self.book_manager.update_order(order, match_size)

    if order.status == "filled":
      logger.info("Match filled order")
      self.handle_full_match(order)

    else:
      logger.info("Match filled {} of order, {} is remaining."
                  .format(Decimal(match_size), order.size - order.filled))

    self.book_manager.close_book()

  def handle_full_match(self, order):
    if order.side == "buy":
      # a buy order triggers listing sells and vise versa
      self.start_sell_thread(order)
    else:
      self.start_buy_thread(order)

  def start_initial_trade_thread(self):
    self.initial_thread = TradingThread(self.book_manager)
    self.initial_thread.start()

  def start_sell_thread(self, order):
    self.clean_thread_pools()
    thread = TradingThread(self.book_manager, order)
    if self.initial_thread is not None and not self.initial_done:
      self.pause_initial_thread(thread)
    for other_thread in self._sell_threads:
      other_thread.intervene(order.size, thread)
    for other_thread in self._buy_threads:
      # pause thread but do not override it with larger size
      other_thread.intervene(0, thread)
    thread.start()
    self._sell_threads.append(thread)

  def start_buy_thread(self, order):
    self.clean_thread_pools()
    thread = TradingThread(self.book_manager, order)
    if self.initial_thread is not None and not self.initial_done:
      self.pause_initial_thread(thread)
    for other_thread in self._buy_threads:
      other_thread.intervene(order.size, thread)
    for other_thread in self._sell_threads:
      # pause thread but do not override it with larger size
      other_thread.intervene(0, thread)
    thread.start()
    self._buy_threads.append(thread)

  def pause_initial_thread(self, thread):
    if self.initial_thread.is_alive():
      self.initial_thread.intervene((0, thread))
    else:
      self.initial_done = True

  def clean_thread_pools(self):
    self._sell_threads = [t for t in self._sell_threads if t.is_alive()]
    self._buy_threads = [t for t in self._buy_threads if t.is_alive()]


class TradingThread(threading.Thread):

  def __init__(self, book_manager, filled_order=None):

    super().__init__()

    self.filled_order = filled_order
    self.book_manager = book_manager
    self.adjust_queue = queue.Queue()
    self.started = False

  def start(self):
    self.started = True
    super().start()

  def has_not_started(self):
    return not self.started

  def run(self):
    self.book_manager.load_book()
    if self.filled_order is None:
      self.book_manager.send_orders(adjust_queue=self.adjust_queue)
    else:
      self.book_manager.send_trade_sequence(self.filled_order,
                                            adjust_queue=self.adjust_queue)
    self.book_manager.close_book()

  def intervene(self, size, other_thread):
    """
    Intervene will signal to the thread that another thread is going to start
    and will post from the minimum size to the given size. This thread will use
    the size to determine if it should stop or pause and will start again once
    the given thread is done using the join method.
    :param size: max_size of other thread
    :param other_thread: other thread
    :return:
    """
    self.adjust_queue.put((size, other_thread))

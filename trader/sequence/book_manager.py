from decimal import Decimal
import logging
import logging.config
from pprint import pformat
import time

from sqlalchemy.exc import OperationalError

import config
from trader.exchange.api_wrapper.exchange_api import ExchangeApi
from trader.exchange.api_wrapper.noop_trader import NoopApi
from trader.exchange.persisted_book import Book
from trader.exchange.order import Order
from trader.database.db import dal
from trader.sequence.abstract_book_manager import AbstractBookManager


logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class book_manager_maker:

  def __init__(
    self,
    terms,
    book=None,
    trading_api=NoopApi(),
    persist=True):

    kw = dict()
    kw["terms"] = terms

    if book is None:
      book = Book(terms.pair)

    if not isinstance(trading_api, ExchangeApi):
      raise ValueError("trader {} is not an instance of ExchangeApi",
                       str(trading_api))
    kw["trading_api"] = trading_api

    kw["persist"] = persist
    session = None
    if persist:
      # if they do not exist, this will create tables
      try:
        dal.connect()
        session = dal.Session()
        session.add(book)
        session.commit()
        kw["book_id"] = book.id
      except OperationalError as e:
        session.rollback()
        logger.error("Initial db connection failed")
        raise e
    else:
      kw["book"] = book

    self.kw = kw

    # initialize book
    bm = BookManager(**self.kw)
    if session is not None:
      bm.load_book(session)
    bm.initialize_book()
    bm.close_book()

  def __call__(self):
    return BookManager(**self.kw)


class BookManager(AbstractBookManager):

  def __init__(self,
               terms,
               book_id=None,
               book=None,
               trading_api=NoopApi(),
               persist=True):

    self.terms = terms
    self.book_id = book_id
    self.persist = persist
    self.book_id = book_id
    self.book = book
    self.trading_api = trading_api

    self.adjust_queue = None
    self.session = None
    self.is_retry = False

  def load_book(self, session=None):
    try:
      if self.book_id is None:
        logger.error("persist set to {}".format(self.persist))
        raise RuntimeError("BookManager has no book id this may be because "
                           "persist is set to false")
      if session is None:
        self.session = dal.Session()
      else:
        self.session = session
      self.book = self.session.query(Book).filter(Book.id == self.book_id).one()

    except OperationalError as e:
      logger.warning("OperationError: {} ".format(e.args))
      self.session.rollback()
      raise e  # This gets raised to thread handler to reconnect

    except Exception as e:
      logger.error("Rolling back book load {}".format(e.args))
      self.session.rollback()
      raise e  # This gets raised

  def close_book(self):
    if self.session is not None:
      self.session.commit()
      self.session.close()
      self.session = None

  def commit(self):
    if self.session is not None:
      try:
        self.session.commit()
      except OperationalError as e:
        logger.warning("OperationError: {} ".format(e.args))
        self.session.rollback()
        raise e
      except Exception as e:
        logger.error("Rolling back commit: {}".format(e.args))
        self.session.rollback()
        raise e

  def look_for_order(self, match):
    try:
      return next(
        o for o in self.book.get_open_orders()
        if o.exchange_id == match["maker_order_id"]
      )
    except StopIteration:
      return None

  def set_adjust_queue(self, adjust_queue):
    self.adjust_queue = adjust_queue

  def get_terms_min_size(self):
    return self.terms.min_size

  def get_terms_size_change(self):
    return self.terms.size_change

  def is_trading_api_test(self):
    return self.trading_api.test

  def initialize_book(self):
    """Creates a book and the appropriate pending orders associated with the
    Book_Manager.terms and saves them to the database.
    """
    first_buy_price = self.terms.mid_price - self.terms.price_change
    first_sell_price = self.terms.mid_price + self.terms.price_change
    first_buy_size = (self.terms.min_size + self.terms.size_change *
                      self.terms.skew)

    if self.terms.skew < 0:
      raise NotImplemented("More buys then sells, not implemented yet")

    elif self.terms.skew > 0:
      # Add skewed orders and reset initial sell price and sell size
      first_sell_size = self.terms.min_size
      self.add_orders('sell',
                      self.terms.skew,
                      first_sell_size,
                      first_sell_price,
                      self.terms.size_change
                      )
      # Reset initials for remainder of trades
      first_sell_price += self.terms.price_change * self.terms.skew
      first_sell_size += self.terms.size_change * (self.terms.skew + 1)
    else:
      first_sell_size = self.terms.min_size + self.terms.size_change

    self.add_orders("buy",
                    self.terms.buy_count,
                    first_buy_size,
                    first_buy_price,
                    self.terms.size_change * 2
                    )
    self.add_orders("sell",
                    self.terms.sell_count - self.terms.skew,
                    first_sell_size,
                    first_sell_price,
                    self.terms.size_change * 2
                    )

  def add_orders(self, side, count, first_size, first_price, size_change):
    """
    helper method to add orders to the book
    """
    price = first_price
    size = first_size
    plus_or_minus = -1 if side == "buy" else 1
    for i in range(count):
      order = Order(
        self.terms.pair, side, size, price, post_only=True,
      )
      self.book.add_order_to_book(order)
      logger.debug("Adding a {} {} order size {} and price {}". format(
        side, self.terms.pair, size, price))

      new_size = size + size_change
      size = round(new_size, 8)
      new_price = price + plus_or_minus * self.terms.price_change
      price = round(new_price, self.terms.price_decimals)

  def send_orders(self, adjust_queue=None):
    """
    Method used by the socket to send orders once the socket has started
    to consume messages. Sends all pending orders created at initialization.
    Creates a session to update the database.
    """
    if self.book is None:
      raise ValueError("Book may not have been loaded")
    ready_orders = self.book.get_ready_orders()
    buys = [o for o in ready_orders if o.side == "buy"]
    sells = [o for o in ready_orders if o.side == "sell"]
    pick_sell = True
    max_size = self.terms.min_size + (self.terms.count - 1) * self.terms.size_change
    while len(buys) + len(sells) > 0:
      if adjust_queue is not None and not adjust_queue.empty():
        # Another thread is taking priority stopping or pausing
        while not adjust_queue.empty():
          other_max_size, other_thread = adjust_queue.get()
          logging.warning("Thread with Initial thread being adjusted by "
                          "priority {}"
                          .format(other_max_size))
          if other_max_size >= max_size:
            # Stop this thread work will be reproduced other thread
            return
          while other_thread.has_not_started() and not other_thread.is_alive():
            # wait for other thread to start before joining
            time.sleep(.01)
          # pause thread until other thread is complete
          other_thread.join()

      if pick_sell and len(sells) > 0:
        order = sells.pop(0)
        if len(buys) != 0:
          pick_sell = False
      else:
        order = buys.pop(0)
        if len(sells) != 0:
          pick_sell = True
      self.send_order(order)
      time.sleep(.2)

  def send_order(self, order):
    self.trading_api.send_order(order)
    if order.status == "rejected":
      if order.post_only and order.reject_reason == "post only":
        # Find first price available for post-only
        logger.warning("Post-only rejected:\n" + pformat(str(order)))
        # Adjust and retry until confirm happens
        self.post_at_best_post_only(order)
        return
      else:
        logger.error("Exchange rejected order for the following reason: {}"
                     .format(order.rejected_reason))
    self.trading_api.confirm_order(order)
    if not order.status in ["open", "filled"]:
      logger.error("Received {} status when sending order:\n".format(
        order.status) + pformat(order)
                   )
    self.commit()

  def update_order(self, order, match_size):
    order_filled = False
    order.filled += match_size
    if order.filled == order.size:
      order.status = "filled"
      order_filled = True
    self.commit()
    return order_filled

  def cancel_sent_order(self, order):
    self.trading_api.cancel_order(order)
    self.commit()

  def cancel_all_orders(self):
    if self.persist:
      self.load_book()
    self.cancel_order_list(self.book.get_open_orders())
    if self.persist:
      self.close_book()

  def cancel_order_list(self, order_list):
    for order in order_list:
      self.cancel_sent_order(order)

  def cancel_order_by_attribute(self, side, size):
    """
    Cancels order of matching side and size. When more than one, the oldest
    order will be canceled.
    """
    matched_orders = [
      o for o in self.book.get_open_orders()
      if o.side == side and o.size == size
    ]
    if len(matched_orders) == 0:
      logger.info("could not find order on {} side and {} size"
                  .format(side, size))
      return
    elif len(matched_orders) > 1:
      logger.warning("Found more than one trade to cancel: {}"
                     .format([o.exchange_id for o in matched_orders]))
      for o in matched_orders:
        logger.debug("One of orders found to cancel {}".format(o.exchange_id))
        self.cancel_sent_order(o)
    else:
      order_to_cancel = matched_orders[0]
      logging.debug("Found order to cancel {}"
                    .format(order_to_cancel.exchange_id))
      self.cancel_sent_order(order_to_cancel)

  def send_trade_sequence(self, filled_order_desc, adjust_queue=None):
    """
    When an open order is matched, the matched value is distributed across the
    opposite side trades by adjusting all of those smaller then the matched
    trade by the size change. To do this, each trade must be canceled and
    posted again at the adjusted amount.
    """
    side, count, price = self.get_sequence_parameter(filled_order_desc)
    size = self.get_terms_min_size()
    logger.info("Adjusting Orders")
    logger.debug("side: {}, count: {}, price {}".format(side, count, price))

    max_size = size + (count - 1) * self.terms.size_change
    plus_or_minus = -1 if side == "buy" else 1
    for i in range(count):
      # Check queue for new threads
      if adjust_queue is not None and not adjust_queue.empty():
        # Another thread is taking priority stopping or pausing
        while not adjust_queue.empty():
          other_max_size, other_thread = adjust_queue.get()
          logging.warning("Thread with max size {} being adjusted by {}"
                       .format(max_size, other_max_size))
          if other_max_size >= max_size:
            # Stop this thread work will be reproduced other thread
            return
          while other_thread.has_not_started() and not other_thread.is_alive():
            # wait for other thread to start before joining
            time.sleep(.01)
          # pause thread until other thread is complete
          other_thread.join()

      # Main logic of canceling thread
      if count == 1:
        # one trade means that the first size does not need to be canceled
        self.add_and_send_order(side, size, price)
      else:
        self.cancel_order_by_attribute(side, size)
        self.add_and_send_order(side, size, price)
        price = price + (plus_or_minus * self.terms.price_change)
        size = size + self.terms.size_change
        # CoinbasePro API is rate limited, need to slow down accordingly.
        time.sleep(.2)

  def add_and_send_order(self, side, size, price):
    order = Order(self.terms.pair, side, size, price)
    self.book.add_order_to_book(order)
    # Recursion may override this order
    self.send_order(order)

  def post_at_best_post_only(self, order):
    # if we are buying we want minus, if we are selling we want plus
    details = self.trading_api.get_product_details(self.terms.pair)
    plus_or_minus = -1 if order.side == "buy" else 1
    adjust = plus_or_minus * Decimal(details["quote_increment"])
    ask, bid = self.trading_api.get_first_book(self.terms.pair)
    order.price = (Decimal(bid[0][0]) + adjust if order.side == "buy" else
                   Decimal(ask[0][0]) + adjust)
    self.send_order(order)

  def get_sequence_parameter(self, order_description):
    side, plus_minus = ("buy", -1) if order_description["side"] == "sell" else \
      ("sell", 1)
    count = int(
      1 + (order_description["size"] - self.get_terms_min_size()) /
      self.get_terms_size_change()
    )
    first_price = order_description["price"] + plus_minus * \
                  self.terms.price_change
    return side, count, first_price

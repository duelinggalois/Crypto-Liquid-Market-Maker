import abc

from trader.exchange.api_wrapper.exchange_api import ExchangeApi
from trader.exchange.api_wrapper.noop_trader import NoopApi
from trader.exchange.persisted_book import Book


class AbstractBookManager(abc.ABC):

  @abc.abstractmethod
  def load_book(self):
    pass

  @abc.abstractmethod
  def close_book(self):
    pass

  @abc.abstractmethod
  def add_orders(self, side, count, first_size, first_price, size_change):
    pass

  @abc.abstractmethod
  def send_orders(self):
    pass

  @abc.abstractmethod
  def add_and_send_order(self, side, size, price):
    pass

  @abc.abstractmethod
  def post_at_best_post_only(self, order):
    pass

  @abc.abstractmethod
  def send_order(self, order):
    pass

  @abc.abstractmethod
  def update_order(self, order, match_size):
    pass

  @abc.abstractmethod
  def cancel_all_orders(self):
    pass

  @abc.abstractmethod
  def cancel_order_list(self, order_list):
    pass

  @abc.abstractmethod
  def cancel_sent_order(self, order):
    pass

  @abc.abstractmethod
  def look_for_order(self, match):
    pass

  @abc.abstractmethod
  def cancel_order_by_attribute(self, side, size):
    pass

  @abc.abstractmethod
  def send_trade_sequence(self, filled_order):
    """
    Sends trades in a sequence in response to a filled trade. The first size
    will be the terms minimum size and each trade following will be larger
    according terms size increase.

    :param filled_order: order to respond to
    :return: None
    """
    pass

  @abc.abstractmethod
  def set_adjust_queue(self, adjust_queue):
    """
    used to set an queue to send messages from outside to the inside of a
    thread running the send_trade_sequence method. The message will be used to
    pause or stop the thread.
    :param adjust_queue: a queue to carry messages
    :return: None
    """
    self.adjust_queue = adjust_queue

  @abc.abstractmethod
  def get_terms_min_size(self):
    return self.terms.min_size

  @abc.abstractmethod
  def get_terms_size_change(self):
    return self.terms.size_change

  @abc.abstractmethod
  def is_trading_api_test(self):
    return self.trading_api.test

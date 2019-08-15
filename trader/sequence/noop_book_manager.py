from trader.exchange.api_wrapper.noop_trader import NoopApi
from trader.sequence.abstract_book_manager import AbstractBookManager
from trader.sequence.book_manager import BookManager


class noop_book_manager_maker:

  def __init__(
    self,
    terms,
    book=None,
    ):

    kw = dict()
    kw["terms"] = terms
    kw["book"] = book

    bm = NoopBookManager(**kw)
    bm.initialize_book()

    self.kw = kw

  def __call__(self):
    return NoopBookManager(**self.kw)


class NoopBookManager(AbstractBookManager):

  def __init__(self, terms, book=None):
    # Keeping some functionality while discarding what is not needed for
    # testing
    self.book = book
    self.bm = BookManager(terms, book=book, persist=False)
    self.adjust_queue = None

  def initialize_book(self):
    self.bm.initialize_book()

  def load_book(self):
    pass

  def close_book(self):
    pass

  def add_orders(self, side, count, first_size, first_price, size_change):
    self.bm.add_orders(side, count, first_size, first_price, size_change)

  def send_orders(self):
    self.bm.send_orders()

  def add_and_send_order(self, side, size, price):
    self.bm.add_and_send_order(side, size, price)

  def post_at_best_post_only(self, order):
    self.bm.post_at_best_post_only(order)

  def send_order(self, order):
    self.bm.send_order(order)

  def update_order(self, order, match_size):
    return self.bm.update_order(order, match_size)

  def cancel_all_orders(self):
    pass

  def cancel_order_list(self, order_list):
    pass

  def cancel_sent_order(self, order):
    pass

  def look_for_order(self, match):
    return self.bm.look_for_order(match)

  def cancel_order_by_attribute(self, side, size):
    self.bm.cancel_order_by_attribute(side, size)

  def send_trade_sequence(self, filled_order, adjust_queue=None):
    self.bm.send_trade_sequence(filled_order, adjust_queue=adjust_queue)

  def set_adjust_queue(self, adjust_queue):
    self.bm.set_adjust_queue(adjust_queue)

  def get_terms_min_size(self):
    self.bm.get_terms_min_size()

  def get_terms_size_change(self):
    self.bm.get_terms_size_change()

  def is_trading_api_test(self):
    self.bm.is_trading_api_test()


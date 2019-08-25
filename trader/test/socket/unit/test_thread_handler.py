import time
import unittest
from decimal import Decimal

import config
from trader.exchange.api_enum import ApiEnum
from trader.exchange.api_provider import ApiProvider
from trader.exchange.noop_book import NoopBook
from trader.operations.noop_book_manager import noop_book_manager_maker
from trader.database.models.trading_terms import TradingTerms
from trader.socket.thread_handler import ThreadHandler
from trader.test.common_utils import create_match, create_last_match


class TestThreadHandler(unittest.TestCase):
  """
     Test case set up
     | price | size | value |
     |   900 |  1.7 |   850 |
     |   800 |  1.5 |   750 |
     |   700 |  1.3 |   650 |
     |   600 |  1.1 |   550 |
     |   500 |      |       |
     |   400 |  1.0 |   400 |
     |   300 |  1.2 |   360 |
     |   200 |  1.4 |   280 |
     |   100 |  1.6 |   160 |
          | sbtotal |  4000 |
          | fee     |    12 |
          | total   |  4012 |
     """

  def setUp(self):
    low_price = "100"
    budget = Decimal("4000") * (1 + Decimal(config.CB_FEE))
    ApiProvider.noop_api.set_noop_parameters(["500"], ["BTC-USD"])
    self.book = NoopBook("BTC-USD")
    self.terms = TradingTerms(
      "BTC-USD", budget, "1", ".1", low_price, api_enum=ApiEnum.NoopApi
    )
    self.NoopBookManagerMaker = noop_book_manager_maker(self.terms,
                                                        book=self.book)
    self.thread_handler = ThreadHandler()
    self.thread_handler.add_terms(self.terms,
                                  BookManagerMaker=self.NoopBookManagerMaker)
    self.book_manager = self.NoopBookManagerMaker()

  def tearDown(self):
    ApiProvider.noop_api.reset_noop()

  def test_handle_last_match_message(self):
    self.send_last_match_message()

    expected_orders = {
      ('buy', '100.00', '1.60000000'),
      ('buy', '200.00', '1.40000000'),
      ('buy', '300.00', '1.20000000'),
      ('buy', '400.00', '1.00000000'),
      ('sell', '600.00', '1.10000000'),
      ('sell', '700.00', '1.30000000'),
      ('sell', '800.00', '1.50000000'),
      ('sell', '900.00', '1.70000000')
    }
    actual_orders = {(o.side, str(o.price), str(o.size)) for o in
                     self.book_manager.book.get_open_orders()}
    self.assertEqual(actual_orders, expected_orders)

  def test_remove_terms(self):
    self.send_last_match_message()
    self.thread_handler.remove_terms(self.terms)
    self.wait_for_threads()
    expected_orders = set()
    actual_orders = {(o.side, str(o.price), str(o.size)) for o in
                     self.book_manager.book.get_open_orders()}
    self.assertEqual(actual_orders, expected_orders)
    expected_canceled_order = {
      ('buy', '100.00', '1.60000000'),
      ('buy', '200.00', '1.40000000'),
      ('buy', '300.00', '1.20000000'),
      ('buy', '400.00', '1.00000000'),
      ('sell', '600.00', '1.10000000'),
      ('sell', '700.00', '1.30000000'),
      ('sell', '800.00', '1.50000000'),
      ('sell', '900.00', '1.70000000')
    }
    actual_canceled = {(o.side, str(o.price), str(o.size)) for o in
                       self.book_manager.book.get_canceled_orders()}

    self.assertEqual(actual_canceled, expected_canceled_order)

  def test_intervene_initial_thread(self):
    self.thread_handler.handle_last_match_message(create_last_match())
    match, buy_order = self.create_match_from_size("1")
    self.thread_handler.check_book_for_match(match)
    self.wait_for_threads()
    expected_order = {('sell', '600.00', '1.10000000'),
                      ("sell", "700.00", "1.30000000"),
                      ("buy", "300.00", "1.20000000"),
                      ("sell", "800.00", "1.50000000"),
                      ("buy", "200.00", "1.40000000"),
                      ("sell", "900.00", "1.70000000"),
                      ("buy", "100.00", "1.60000000"),
                      ("sell", "500.00", "1")
                      }
    actual_order = {(o.side, str(o.price), str(o.size)) for o in
                    self.book_manager.book.get_open_orders()}
    self.assertEqual(actual_order, expected_order)
    self.assertEqual(self.book_manager.book.get_filled_orders(), [buy_order])

  def test_thread_check_book_for_buy_match(self):
    self.send_last_match_message()

    match, buy_order = self.create_match_from_size("1")
    self.thread_handler.check_book_for_match(match)
    self.wait_for_threads()

    expected_order = {('sell', '600.00', '1.10000000'),
                      ("sell", "700.00", "1.30000000"),
                      ("buy", "300.00", "1.20000000"),
                      ("sell", "800.00", "1.50000000"),
                      ("buy", "200.00", "1.40000000"),
                      ("sell", "900.00", "1.70000000"),
                      ("buy", "100.00", "1.60000000"),
                      ("sell", "500.00", "1")
                      }
    actual_order = {(o.side, str(o.price), str(o.size)) for o in
                    self.book_manager.book.get_open_orders()}
    self.assertEqual(actual_order, expected_order)
    self.assertEqual(self.book_manager.book.get_filled_orders(), [buy_order])

  def test_thread_check_book_for_sell_match(self):
    self.send_last_match_message()
    match, sell_order = self.create_match_from_size("1.1")
    self.thread_handler.check_book_for_match(match)
    self.wait_for_threads()

    expected_orders = {
      ("sell", "900.00", "1.70000000"),
      ("sell", "800.00", "1.50000000"),
      ("sell", "700.00", "1.30000000"),
      ("buy", "500.00", "1"),
      ("buy", "400.00", "1.10000000"),
      ("buy", "300.00", "1.20000000"),
      ("buy", "200.00", "1.40000000"),
      ("buy", "100.00", "1.60000000"),
    }
    actual_order = {(o.side, str(o.price), str(o.size)) for o in
                    self.book_manager.book.get_open_orders()}
    self.assertEqual(actual_order, expected_orders)
    self.assertEqual(self.book_manager.book.get_filled_orders(), [sell_order])

  def test_skip_threads(self):
    self.send_last_match_message()
    # executing four sell trades will skip test killing threads
    match_1, order_1 = self.create_match_from_size("1.1")
    match_2, order_2 = self.create_match_from_size("1.3")
    match_3, order_3 = self.create_match_from_size("1.5")
    match_4, order_4 = self.create_match_from_size("1.7")

    self.thread_handler.check_book_for_match(match_1)
    self.thread_handler.check_book_for_match(match_2)
    self.thread_handler.check_book_for_match(match_3)
    self.thread_handler.check_book_for_match(match_4)

    self.wait_for_threads()

    expected_orders = {
      ("buy", "800.00", "1"),
      ("buy", "700.00", "1.10000000"),
      ("buy", "600.00", "1.20000000"),
      ("buy", "500.00", "1.30000000"),
      ("buy", "400.00", "1.40000000"),
      ("buy", "300.00", "1.50000000"),
      ("buy", "200.00", "1.60000000"),
      ("buy", "100.00", "1.70000000"),
    }

    actual_order = {(o.side, str(o.price), str(o.size)) for o in
                    self.book_manager.book.get_open_orders()}
    self.assertEqual(actual_order, expected_orders)
    self.assertEqual(self.book_manager.book.get_filled_orders(),
                     [order_1, order_2, order_3, order_4])

  def test_back_and_forth_threads(self):
    self.send_last_match_message()
    # size 1.1 and 1.3 sold
    match_1, order_1 = self.create_match_from_size("1.1", "sell", "600")
    match_2, order_2 = self.create_match_from_size("1.3", "sell", "700")
    self.thread_handler.check_book_for_match(match_1)
    self.thread_handler.check_book_for_match(match_2)

    # size 1 and 1.1 bought if these wait to get the higher priced trades,
    # race conditions of selecting the lower price trade and then it getting
    # canceled are avoided. these conditions are not possible in real life
    # as an order can not be picked to be filled, canceled and then attempted
    # to be filled as in this test
    match_3, order_3 = self.create_match_from_size("1", "buy", "600")
    match_4, order_4 = self.create_match_from_size("1.1", "buy", "500")
    self.thread_handler.check_book_for_match(match_3)
    self.thread_handler.check_book_for_match(match_4)

    # size 1 and 1.1 sold
    match_5, order_5 = self.create_match_from_size("1", "sell", "600")
    match_6, order_6 = self.create_match_from_size("1.1", "sell", "500")
    self.thread_handler.check_book_for_match(match_5)
    self.thread_handler.check_book_for_match(match_6)

    self.wait_for_threads()

    expected_orders = {
      ("sell", "900.00", "1.70000000"),
      ("sell", "800.00", "1.50000000"),
      ("buy", "600.00", "1"),
      ("buy", "500.00", "1.10000000"),
      ("buy", "400.00", "1.20000000"),
      ("buy", "300.00", "1.30000000"),
      ("buy", "200.00", "1.40000000"),
      ("buy", "100.00", "1.60000000"),
    }

    actual_order = {(o.side, str(o.price), str(o.size)) for o in
                    self.book_manager.book.get_open_orders()}
    self.assertEqual(actual_order, expected_orders)
    self.assertEqual(self.book_manager.book.get_filled_orders(),
                     [order_1, order_2, order_3, order_4, order_5, order_6])

  def send_last_match_message(self):
    self.thread_handler.handle_last_match_message(create_last_match())
    self.assertEqual(len(self.thread_handler.get_all_immutable_threads()), 1)
    thread = self.thread_handler.get_all_immutable_threads()[0]
    thread.join()

  def wait_for_threads(self):
    for thread in self.thread_handler.get_all_threads():
      if thread is not None:
        thread.join()

  def create_match_from_size(self, size, side=None, price=None):
    """
    Check for match will grab a matching open order and create a match for it
    the recursive loop is due to race conditions of threads and needing to
    wait until the
    :param size: Order Size
    :param side: Order Side
    :param price: Order Price
    :return: Dictionary
    """
    start = time.time()
    try:
      order = next(
        o for o in self.book_manager.book.get_open_orders()
        if o.size == Decimal(size) and (side is None or o.side == side) and
        (price is None or o.price == Decimal(price))
      )
    except StopIteration:
      if time.time() - start < 1:
        time.sleep(.005)
        return self.create_match_from_size(size)
      else:
        raise TimeoutError("Could not find order after waiting 10 seconds.")
    return create_match(order), order

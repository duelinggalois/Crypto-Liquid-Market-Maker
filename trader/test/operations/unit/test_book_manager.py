from decimal import Decimal
import unittest

import config
from trader.exchange.api_enum import ApiEnum
from trader.exchange.api_provider import ApiProvider
from trader.exchange.noop_book import NoopBook
from trader.operations.book_manager import book_manager_maker
from trader.database.models import trading_terms
from trader.test.common_utils import create_match


class TestBookManager(unittest.TestCase):

  def setUp(self):
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

    low_price = "100"
    budget = Decimal("4000") * (1 + Decimal(config.CB_FEE))
    ApiProvider.noop_api.set_noop_parameters(["500"], ["BTC-USD"])
    self.terms = trading_terms.TradingTermsBase(
      "BTC-USD", budget, "1", ".1", low_price, api_enum=ApiEnum.NoopApi
    )
    book = NoopBook("BTC-USD")
    self.BookManagerMaker = book_manager_maker(
      self.terms, persist=False, book=book, trading_api=ApiProvider.noop_api)
    self.book_manager = self.BookManagerMaker()

  def tearDown(self):
    ApiProvider.noop_api.reset_noop()

  def test_BookManager_init(self):
    self.assertEqual(self.terms, self.book_manager.terms)

    book = self.book_manager.book
    self.assertEqual(book.pair, "BTC-USD")

    buy_list = [round(order.price * order.size, 2)
                for order in book.get_ready_orders()
                if order.side == "buy"]
    buy_budget = round(sum(buy_list), 2)

    sell_list = [order.size for order in book.get_ready_orders()
                 if order.side == "sell"]
    sell_budget = sum(sell_list) * self.terms.mid_price
    sell_budget = round(sell_budget, 2)
    budget_without_fee = sell_budget + buy_budget

    self.assertEqual(budget_without_fee, self.terms.budget /
                     (1 + Decimal(config.CB_FEE)))
    self.assertEqual(len(self.book_manager.book.get_ready_orders()), 8)
    actual_order = [(o.side, str(o.price), str(o.size)) for o in
                    self.book_manager.book.get_ready_orders()]
    expected_order = [("buy", "400.00", "1.00000000"),
                      ("buy", "300.00", "1.20000000"),
                      ("buy", "200.00", "1.40000000"),
                      ("buy", "100.00", "1.60000000"),
                      ("sell", "600.00", "1.10000000"),
                      ("sell", "700.00", "1.30000000"),
                      ("sell", "800.00", "1.50000000"),
                      ("sell", "900.00", "1.70000000"),
                      ]
    self.assertEqual(expected_order, actual_order)

  def test_BookManager_send_orders(self):
    self.book_manager.send_orders()
    self.assertEqual(self.book_manager.book.get_ready_orders(), [])
    actual_orders = {(o.side, str(o.price), str(o.size)) for o in
                     self.book_manager.book.get_open_orders()}
    expected_orders = {("sell", "600.00", "1.10000000"),
                       ("buy", "400.00", "1.00000000"),
                       ("sell", "700.00", "1.30000000"),
                       ("buy", "300.00", "1.20000000"),
                       ("sell", "800.00", "1.50000000"),
                       ("buy", "200.00", "1.40000000"),
                       ("sell", "900.00", "1.70000000"),
                       ("buy", "100.00", "1.60000000"),
                      }
    self.assertEqual(actual_orders, expected_orders)

  def test_BookManager_adjust_orders_for_matched_trade_matched_buy(self):
    self.book_manager.send_orders()

    buy_order = self.filled_trade_response_check_using_size("1")

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

  def test_BookManager_adjust_orders_for_matched_trade_matched_sell(self):
    self.book_manager.send_orders()

    expected_canceled_order = next(o for o in self.book_manager.book.get_open_orders() if
                                   o.size == Decimal("1"))

    sell_order = self.filled_trade_response_check_using_size("1.1")

    actual_orders = {(o.side, str(o.price), str(o.size)) for o in
                     self.book_manager.book.get_open_orders()}
    expected_orders = {("sell", "700.00", "1.30000000"),
                      ("buy", "300.00", "1.20000000"),
                      ("sell", "800.00", "1.50000000"),
                      ("buy", "200.00", "1.40000000"),
                      ("sell", "900.00", "1.70000000"),
                      ("buy", "100.00", "1.60000000"),
                      ("buy", "500.00", "1"),
                      ("buy", "400.00", "1.10000000")
                      }
    self.assertEqual(actual_orders, expected_orders)
    self.assertEqual(self.book_manager.book.get_canceled_orders(), [expected_canceled_order])
    self.assertEqual(self.book_manager.book.get_filled_orders(), [sell_order])

  def test_BookManager_when_full_match_three_buys(self):
    self.book_manager.send_orders()

    first_order = self.filled_trade_response_check_using_size("1")
    second_order = self.filled_trade_response_check_using_size("1.2")
    third_order = self.filled_trade_response_check_using_size("1.4")

    actual_order = {(o.side, str(o.price), str(o.size)) for o in
                    self.book_manager.book.get_open_orders()}
    expected_order = {("sell", "800.00", "1.50000000"),
                      ("sell", "900.00", "1.70000000"),
                      ("buy", "100.00", "1.60000000"),
                      ("sell", "300.00", "1"),
                      ('sell', '400.00', '1.10000000'),
                      ("sell", "500.00", "1.20000000"),
                      ("sell", "600.00", "1.30000000"),
                      ('sell', '700.00', '1.40000000'),
                      }
    self.assertEqual(actual_order, expected_order)
    self.assertEqual(self.book_manager.book.get_filled_orders(), [
      first_order, second_order, third_order
    ])

  def test_BookManager_when_full_match_three_sells(self):
    self.book_manager.send_orders()

    first_order = self.filled_trade_response_check_using_size("1.1")
    second_order = self.filled_trade_response_check_using_size("1.3")
    third_order = self.filled_trade_response_check_using_size("1.5")

    actual_order = {(o.side, str(o.price), str(o.size)) for o in
                    self.book_manager.book.get_open_orders()}
    expected_order = {("sell", "900.00", "1.70000000"),
                      ("buy", "100.00", "1.60000000"),
                      ("buy", "700.00", "1"),
                      ("buy", "600.00", "1.10000000"),
                      ("buy", "500.00", "1.20000000"),
                      ("buy", "400.00", "1.30000000"),
                      ("buy", "300.00", "1.40000000"),
                      ("buy", "200.00", "1.50000000"),
                      }
    self.assertEqual(actual_order, expected_order)
    self.assertEqual(self.book_manager.book.get_filled_orders(), [
      first_order, second_order, third_order
    ])

  def filled_trade_response_check_using_size(self, size):

    order = next(
      o for o in self.book_manager.book.get_open_orders()
      if o.size == Decimal(size)
    )
    match = create_match(order)
    self.assertTrue(self.book_manager.look_for_order(match), order)

    self.assertTrue(self.book_manager.update_order(order, match["size"]))
    order_desc = {
      "side": order.side,
      "size": order.size,
      "price": order.price
    }
    self.book_manager.send_trade_sequence(order_desc)

    return order

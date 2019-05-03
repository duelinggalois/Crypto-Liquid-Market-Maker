from decimal import Decimal
import logging
import logging.config
import unittest
from unittest.mock import Mock
import uuid

import config
from ..sequence.book_manager import BookManager
from ..sequence import trading_terms


logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


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
             total |  4000 |
             fee   |    12 |
    """
    trading_terms.trading_mid_market_price = Mock(side_effect=[Decimal("500")])
    self.mid_price = Decimal("500")
    low_price = "100"
    budget = Decimal("4000") * (1 + Decimal(config.CB_FEE))
    self.terms = trading_terms.TradingTerms(
      "BTC-USD", budget, "1", ".1", low_price, test=True
    )
    self.BookManager = BookManager(self.terms, persist=False)
    self.BookManager.book.send_order = Mock(
      side_effect=self.book_send_order_mock)
    self.BookManager.book.trading_cancel_order = Mock()

  # def tearDown(self):
  #   self.BookManager.book.cancel_all_orders()
  #   self.assertEqual(self.BookManager.book.open_orders, [])

  def test_BookManager_init(self):
    self.assertEqual(self.terms, self.BookManager.terms)

    book = self.BookManager.book
    self.assertEqual(book.pair, "BTC-USD")

    buy_list = [round(order.price * order.size, 2)
                for order in book.ready_orders
                if order.side == "buy"]
    buy_budget = round(sum(buy_list), 2)

    sell_list = [order.size for order in book.ready_orders
                 if order.side == "sell"]
    sell_budget = sum(sell_list) * self.terms.mid_price
    sell_budget = round(sell_budget, 2)
    budget_without_fee = sell_budget + buy_budget

    self.assertEqual(budget_without_fee, self.terms.budget /
                     (1 + Decimal(config.CB_FEE)))
    self.assertEqual(len(self.BookManager.book.ready_orders), 8)
    actual_order = [(o.side, str(o.price), str(o.size)) for o in
                    self.BookManager.book.ready_orders]
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
    self.BookManager.send_orders()
    self.assertEqual(self.BookManager.book.ready_orders, [])
    actual_order = [(o.side, str(o.price), str(o.size)) for o in
                    self.BookManager.book.open_orders]
    expected_order = [("sell", "600.00", "1.10000000"),
                      ("buy", "400.00", "1.00000000"),
                      ("sell", "700.00", "1.30000000"),
                      ("buy", "300.00", "1.20000000"),
                      ("sell", "800.00", "1.50000000"),
                      ("buy", "200.00", "1.40000000"),
                      ("sell", "900.00", "1.70000000"),
                      ("buy", "100.00", "1.60000000"),
                      ]
    self.assertEqual(actual_order, expected_order)
    for order in self.BookManager.book.open_orders:
      self.BookManager.book.send_order.assert_any_call(order)

  def test_BookManager_adjust_orders_for_matched_trade_matched_buy(self):
    self.BookManager.send_orders()

    buy_order = next(o for o in self.BookManager.book.open_orders if o.size ==
                     Decimal("1"))
    self.BookManager.book.order_filled(buy_order)
    self.BookManager.adjust_orders_for_matched_trade(
      "sell", 1, Decimal("500")
    )
    actual_order = [(o.side, str(o.price), str(o.size)) for o in
                    self.BookManager.book.open_orders]
    expected_order = [('sell', '600.00', '1.10000000'),
                      ("sell", "700.00", "1.30000000"),
                      ("buy", "300.00", "1.20000000"),
                      ("sell", "800.00", "1.50000000"),
                      ("buy", "200.00", "1.40000000"),
                      ("sell", "900.00", "1.70000000"),
                      ("buy", "100.00", "1.60000000"),
                      ("sell", "500.00", "1")
                      ]
    self.assertEqual(actual_order, expected_order)
    self.assertEqual(self.BookManager.book.filled_orders, [buy_order])
    self.BookManager.book.send_order.assert_any_call(buy_order)
    for order in self.BookManager.book.open_orders:
      self.BookManager.book.send_order.assert_any_call(order)

  def test_BookManager_adjust_orders_for_matched_trade_matched_sell(self):
    self.BookManager.send_orders()
    sell_order = next(o for o in self.BookManager.book.open_orders if o.size ==
                      Decimal("1.1"))
    canceled_order = next(o for o in self.BookManager.book.open_orders if
                          o.size == Decimal("1"))
    self.BookManager.book.order_filled(sell_order)
    self.BookManager.adjust_orders_for_matched_trade(
      "buy", 2, Decimal("500")
    )
    actual_order = [(o.side, str(o.price), str(o.size)) for o in
                    self.BookManager.book.open_orders]
    expected_order = [("sell", "700.00", "1.30000000"),
                      ("buy", "300.00", "1.20000000"),
                      ("sell", "800.00", "1.50000000"),
                      ("buy", "200.00", "1.40000000"),
                      ("sell", "900.00", "1.70000000"),
                      ("buy", "100.00", "1.60000000"),
                      ("buy", "500.00", "1"),
                      ("buy", "400.00", "1.10000000")
                      ]
    self.assertEqual(actual_order, expected_order)
    self.assertEqual(self.BookManager.book.canceled_orders, [canceled_order])
    self.assertEqual(self.BookManager.book.filled_orders, [sell_order])
    self.BookManager.book.trading_cancel_order.assert_any_call(canceled_order)
    self.BookManager.book.send_order.assert_any_call(canceled_order)
    self.BookManager.book.send_order.assert_any_call(sell_order)
    for order in self.BookManager.book.open_orders:
      self.BookManager.book.send_order.assert_any_call(order)

  def test_BookManager_when_full_match_three_buys(self):
    self.BookManager.send_orders()
    first_order = next(o for o in self.BookManager.book.open_orders if
                       o.size == Decimal("1"))
    second_order = next(o for o in self.BookManager.book.open_orders if
                        o.size == Decimal("1.2"))
    third_order = next(o for o in self.BookManager.book.open_orders if
                       o.size == Decimal("1.4"))
    first_open = self.BookManager.book.open_orders.copy()
    self.BookManager.when_full_match(first_order)
    second_open = [o for o in self.BookManager.book.open_orders if o not in
                   first_open]
    self.BookManager.when_full_match(second_order)
    third_open = [o for o in self.BookManager.book.open_orders if o not in
                  first_open and o not in second_open]
    self.BookManager.when_full_match(third_order)
    forth_open = [o for o in self.BookManager.book.open_orders if o not in
                  first_open and o not in second_open and o not in third_open]
    actual_order = [(o.side, str(o.price), str(o.size)) for o in
                    self.BookManager.book.open_orders]
    expected_order = [("sell", "800.00", "1.50000000"),
                      ("sell", "900.00", "1.70000000"),
                      ("buy", "100.00", "1.60000000"),
                      ("sell", "300.00", "1"),
                      ('sell', '400.00', '1.10000000'),
                      ("sell", "500.00", "1.20000000"),
                      ("sell", "600.00", "1.30000000"),
                      ('sell', '700.00', '1.40000000'),
                      ]
    self.assertEqual(actual_order, expected_order)
    self.assertEqual(self.BookManager.book.filled_orders, [
      first_order, second_order, third_order
    ])
    for order in first_open:
      self.BookManager.book.send_order.assert_any_call(order)
    for order in second_open:
      self.BookManager.book.send_order.assert_any_call(order)
    for order in third_open:
      self.BookManager.book.send_order.assert_any_call(order)
    for order in forth_open:
      self.BookManager.book.send_order.assert_any_call(order)
    for order in self.BookManager.book.canceled_orders:
      self.BookManager.book.trading_cancel_order.assert_any_call(order)

  def test_BookManager_when_full_match_three_sells(self):
    self.BookManager.send_orders()
    first_order = next(o for o in self.BookManager.book.open_orders if
                       o.size == Decimal("1.1"))
    second_order = next(o for o in self.BookManager.book.open_orders if
                        o.size == Decimal("1.3"))
    third_order = next(o for o in self.BookManager.book.open_orders if
                       o.size == Decimal("1.5"))
    first_open = self.BookManager.book.open_orders.copy()
    self.BookManager.when_full_match(first_order)
    second_open = [o for o in self.BookManager.book.open_orders if o not in
                   first_open]
    self.BookManager.when_full_match(second_order)
    third_open = [o for o in self.BookManager.book.open_orders if o not in
                  first_open and o not in second_open]
    self.BookManager.when_full_match(third_order)
    forth_open = [o for o in self.BookManager.book.open_orders if o not in
                  first_open and o not in second_open and o not in third_open]
    actual_order = [(o.side, str(o.price), str(o.size)) for o in
                    self.BookManager.book.open_orders]
    expected_order = [("sell", "900.00", "1.70000000"),
                      ("buy", "100.00", "1.60000000"),
                      ("buy", "700.00", "1"),
                      ("buy", "600.00", "1.10000000"),
                      ("buy", "500.00", "1.20000000"),
                      ("buy", "400.00", "1.30000000"),
                      ("buy", "300.00", "1.40000000"),
                      ("buy", "200.00", "1.50000000"),
                      ]
    self.assertEqual(actual_order, expected_order)
    self.assertEqual(self.BookManager.book.filled_orders, [
      first_order, second_order, third_order
    ])
    for order in first_open:
      self.BookManager.book.send_order.assert_any_call(order)
    for order in second_open:
      self.BookManager.book.send_order.assert_any_call(order)
    for order in third_open:
      self.BookManager.book.send_order.assert_any_call(order)
    for order in forth_open:
      self.BookManager.book.send_order.assert_any_call(order)
    for order in self.BookManager.book.canceled_orders:
      self.BookManager.book.trading_cancel_order.assert_any_call(order)

  def book_send_order_mock(self, order):
    logger.debug("MOCK SEND ORDER")
    logger.debug(type(self))
    order.status = "open"
    order.exchange_id = str(uuid.uuid4())
    self.BookManager.book.open_orders.append(order)
    return order

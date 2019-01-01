import time
import unittest
import decimal
from decimal import Decimal

from ..exchange import order
from ..exchange import trading


class Test_Order(unittest.TestCase):
  """Basic test cases."""

  def test_order_to_string(self):
    test_order = order.Order("BTC-USD", "buy", ".05", "6666.67", test=True)
    self.assertEqual(("pair: {}\n"
                      "side: {}\n"
                      "price: {}\n"
                      "size: {}\n"
                      "filled: {}\n"
                      "status: {}\n"
                      "id: {}\n"
                      "test: {}\n"
                      "history: {}\n"
                      "responses: {}").format("BTC-USD",
                                              "buy",
                                              "6666.67",
                                              ".05",
                                              "0",
                                              "created",
                                              "",
                                              "True",
                                              test_order.history,
                                              test_order.responses),
                     str(test_order))

  def test_update_history(self):
    test_order, t = order.Order("BTC-USD", "buy",
                                .05, 6666.67, test=True), time.time()

    self.assertEqual(round(t, 2), round(test_order.history[0]["time"], 2))
    self.assertEqual("Created", test_order.history[0]["status"])

  def test_order_price_percision(self):
    mid = trading.get_mid_market_price("BTC-USD", test=True)
    test = mid - Decimal("1.00001")
    test_order = order.Order("BTC-USD", "buy",
                             .05, test, test=True)

    rounded = round(test, 2)
    self.assertEqual(test_order.price, rounded)

    mid = trading.get_mid_market_price("LTC-BTC", test=True)
    test = mid - Decimal("1.000004")
    test_order = order.Order("LTC-BTC", "buy",
                             .05, test, test=True)

    rounded = round(test, 5)
    self.assertEqual(test_order.price, rounded)

  # TODO: add error checking for exchange products.
  # def test_wrong_pair(self):
  #   with self.assertRaises(ValueError):
  #     order.Order("ZZZ-USD", "buy", .05, 3, test=True)

  def test_wrong_side(self):
    with self.assertRaises(ValueError):
      order.Order("BTC-USD", "but", .05, 3, test=True)

  def test_wrong_size(self):
    with self.assertRaises(decimal.InvalidOperation):
      order.Order("BTC-USD", "buy", "five", 3, test=True)

  def test_wrong_price(self):
    with self.assertRaises(decimal.InvalidOperation):
      order.Order("BTC-USD", "buy", .05, "three", test=True)

  def test_allow_market_trades(self):
    test_order = order.Order("BTC-USD", "buy", 1, 1, test=True)

    self.assertEqual(test_order.post_only, True)

    test_order.allow_market_trade()

    self.assertEqual(test_order.post_only, False)

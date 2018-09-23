from ..exchange import order
from ..exchange import trading
import time
import unittest


class Test_Order(unittest.TestCase):
  """Basic test cases."""

  def test_order_to_string(self):
    test_order = order.Order("BTC-USD", "buy", .05, 6666.67, test=True)
    self.assertEqual("pair: BTC-USD, side: buy, size: 0.05, price: 6666.67",
                     str(test_order))

  def test_update_history(self):
    test_order, t = order.Order("BTC-USD", "buy",
                                .05, 6666.67, test=True), time.time()

    self.assertEqual(round(t, 2), round(test_order.history[0]["time"], 2))
    self.assertEqual("Created", test_order.history[0]["status"])

  def test_order_price_percision(self):
    mid = trading.get_mid_market_price("BTC-USD", test=True)
    test = mid - 1.00001
    test_order = order.Order("BTC-USD", "buy",
                             .05, test, test=True)

    rounded = round(test, 2)
    self.assertEqual(test_order.price, rounded)

    mid = trading.get_mid_market_price("LTC-BTC", test=True)
    test = mid - 1.000004
    test_order = order.Order("LTC-BTC", "buy",
                             .05, test, test=True)

    rounded = round(test, 5)
    self.assertEqual(test_order.price, rounded)

  def test_wrong_pair(self):
    with self.assertRaises(ValueError):
      order.Order("ZZZ-USD", "buy", .05, 3, test=True)

  def test_wrong_side(self):
    with self.assertRaises(ValueError):
      order.Order("BTC-USD", "but", .05, 3, test=True)

  def test_wrong_size(self):
    with self.assertRaises(TypeError):
      order.Order("BTC-USD", "buy", ".05", 3, test=True)

  def test_wrong_price(self):
    with self.assertRaises(TypeError):
      order.Order("BTC-USD", "buy", .05, "3", test=True)

  def test_allow_market_trades(self):
    test_order = order.Order("BTC-USD", "buy", 1, 1, test=True)

    self.assertEqual(test_order.post_only, True)

    test_order.allow_market_trade()

    self.assertEqual(test_order.post_only, False)

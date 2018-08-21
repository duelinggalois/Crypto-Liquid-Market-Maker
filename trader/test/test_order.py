from ..exchange import order
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

    self.assertEqual(round(t, 4), round(test_order.history[0]["time"], 4))
    self.assertEqual("Created", test_order.history[0]["status"])

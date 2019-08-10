import logging
import unittest
import decimal
from decimal import Decimal

from trader.exchange.order import Order
import config


logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class Test_Order(unittest.TestCase):
  """Basic test cases."""

  def test_order_to_string(self):
    test_order = Order(
      "BTC-USD", "buy", ".05", "6666.67"
    )
    self.assertEqual((
      "pair: {}\n"
      "side: {}\n"
      "price: {}\n"
      "size: {}\n"
      "filled: {}\n"
      "status: {}\n"
      "database_id: {}\n"
      "exchange_id: {}\n"
      # "history: {}\n"
      # "responses: {}"
    ).format(
        "BTC-USD",
        "buy",
        "6666.67",
        "0.05",
        "0",
        "ready",
        "None",
        "None"
        # "[]",
        # "[]"
      ),
      str(test_order))

  def test_update_status(self):
    test_order = Order("BTC-USD", "buy", .05, 6666.67)

    self.assertEqual("ready", test_order.status)

  def test_order_price_percision(self):
    price = Decimal("555.55")
    test_order = Order("BTC-USD", "buy",
                       .05, price)

    self.assertEqual(test_order.price, price)

  def test_wrong_side(self):
    with self.assertRaises(ValueError):
      Order("BTC-USD", "but", .05, 3)

  def test_wrong_size(self):
    with self.assertRaises(decimal.InvalidOperation):
      Order("BTC-USD", "buy", "five", 3)

  def test_wrong_price(self):
    with self.assertRaises(decimal.InvalidOperation):
      Order("BTC-USD", "buy", .05, "three")

  def test_allow_market_trades(self):
    test_order = Order("BTC-USD", "buy", 1, 1)

    self.assertEqual(test_order.post_only, True)

    test_order.allow_market_trade()

    self.assertEqual(test_order.post_only, False)

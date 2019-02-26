import logging
import unittest
import decimal
from decimal import Decimal

from ...order import Order
from ... import trading
import config


logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class Test_Order(unittest.TestCase):
  """Basic test cases."""

  def test_order_to_string(self):
    test_order = Order(
      "BTC-USD", "buy", ".05", "6666.67", persist=False, test=True
    )
    self.assertEqual((
      "pair: {}\n"
      "side: {}\n"
      "price: {}\n"
      "size: {}\n"
      "filled: {}\n"
      "status: {}\n"
      "exchange_id: {}\n"
      "test: {}\n"
      "history: {}\n"
      "responses: {}").format(
        "BTC-USD",
        "buy",
        "6666.67",
        "0.05",
        "0",
        "ready",
        "None",
        "True",
        "[]",
        "[]"
      ),
      str(test_order))

  def test_update_status(self):
    test_order = Order(
      "BTC-USD", "buy",
      .05, 6666.67, persist=False, test=True
    )

    self.assertEqual("ready", test_order.status)

  def test_order_price_percision(self):
    mid = trading.get_mid_market_price("BTC-USD", test=True)
    test = mid / Decimal(".8")
    test_order = Order("BTC-USD", "buy",
                       .05, test, persist=False, test=True)

    rounded = round(test, 2)
    self.assertEqual(test_order.price, rounded)

    mid = trading.get_mid_market_price("ETH-BTC", test=True)
    test = mid / Decimal(".8")
    test_order = Order("ETH-BTC", "buy",
                       .05, test, persist=False, test=True)

    rounded = round(test, 5)
    self.assertEqual(test_order.price, rounded)

  # TODO: add error checking for exchange products.
  # def test_wrong_pair(self):
  #   with self.assertRaises(ValueError):
  #     order.Order("ZZZ-USD", "buy", .05, 3, test=True)

  def test_wrong_side(self):
    with self.assertRaises(ValueError):
      Order("BTC-USD", "but", .05, 3, test=True)

  def test_wrong_size(self):
    with self.assertRaises(decimal.InvalidOperation):
      Order("BTC-USD", "buy", "five", 3, test=True)

  def test_wrong_price(self):
    with self.assertRaises(decimal.InvalidOperation):
      Order("BTC-USD", "buy", .05, "three", test=True)

  def test_allow_market_trades(self):
    test_order = Order("BTC-USD", "buy", 1, 1, persist=False, test=True)

    self.assertEqual(test_order.post_only, True)

    test_order.allow_market_trade()

    self.assertEqual(test_order.post_only, False)

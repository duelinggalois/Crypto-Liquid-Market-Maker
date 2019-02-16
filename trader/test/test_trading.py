from ..exchange import order
from ..exchange import trading
import unittest
import config
import logging
import logging.config


logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class test_trading(unittest.TestCase):

  def setUp(self):
    mid = trading.get_mid_market_price("BTC-USD", test=True)
    if mid > 100000:
      mid = 6000
    self.test_price = round(mid / 2, 2)

    self.test_order = order.Order("BTC-USD",
                                  "buy",
                                  ".011",
                                  self.test_price,
                                  test=True)

  def test_send_order(self):
    trading.send_order(self.test_order)
    response = self.test_order.responses[0]

    self.assertEqual(response["side"], "buy")
    self.assertEqual(response["post_only"], True)
    self.assertEqual(response["type"], "limit")
    self.assertEqual(response["size"], "{:.8f}".format(0.011))
    self.assertEqual(response["price"], "{:.8f}".format(self.test_price))
    self.assertEqual(response["product_id"], "BTC-USD")
    self.assertEqual(response["status"], "pending")
    self.assertEqual(self.test_order.history[0]["status"], "Created")
    self.assertEqual(self.test_order.history[1]["status"], "pending")

    trading.cancel_order(self.test_order)

  def test_cancel_order(self):
    trading.send_order(self.test_order)
    trading.cancel_order(self.test_order)
    response = self.test_order.responses[1]

    self.assertTrue(self.test_order.id not in response)

  def test_get_open_orders(self):
    orders = trading.get_open_orders(pair="BTC-USD", test=True)
    starting_order_ids = {order["id"] for order in orders}
    logger.debug("Starting with {} orders".format(len(starting_order_ids)))

    trading.send_order(self.test_order)
    orders = trading.get_open_orders(pair="BTC-USD", test=True)
    logger.debug("New order {}".format(self.test_order.id))
    new_order_ids = {order["id"] for order in orders}
    logger.debug("Ending with {} orders".format(len(new_order_ids)))

    union_order_ids = starting_order_ids | {self.test_order.id}
    logger.debug("Union has {} orders".format(len(union_order_ids)))

    self.assertEqual(new_order_ids, union_order_ids)

    trading.cancel_order(self.test_order)
    orders = trading.get_open_orders(pair="BTC-USD", test=True)
    new_order_ids = {order["id"] for order in orders}

    self.assertEqual(new_order_ids, starting_order_ids)

  def test_live(self):
    # Check for open orders
    orders = trading.get_open_orders(pair="BTC-USD", test=False)
    starting_order_ids = {order["id"] for order in orders}
    logger.debug("Starting with {} orders".format(len(starting_order_ids)))

    # Check price and send trade at fraction of price
    mid = trading.get_mid_market_price("BTC-USD")
    fraction_of_mid = round(mid / 100, 2)
    self.live_test_order = order.Order("BTC-USD", "buy", ".01",
                                       fraction_of_mid)

    trading.send_order(self.live_test_order)
    orders = trading.get_open_orders(pair="BTC-USD", test=False)
    logger.debug("New order {}".format(self.live_test_order.id))
    new_order_ids = {order["id"] for order in orders}
    logger.debug("Ending with {} orders".format(len(new_order_ids)))

    union_order_ids = starting_order_ids | {self.live_test_order.id}
    logger.debug("Union has {} orders".format(len(union_order_ids)))

    self.assertEqual(new_order_ids, union_order_ids)

    trading.cancel_order(self.live_test_order)
    orders = trading.get_open_orders(pair="BTC-USD", test=False)
    new_order_ids = {order["id"] for order in orders}

    self.assertEqual(new_order_ids, starting_order_ids)

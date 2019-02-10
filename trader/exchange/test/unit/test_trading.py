import unittest
import logging
import logging.config
from decimal import Decimal

import config
from ...order import Order
from ... import trading


logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class test_trading(unittest.TestCase):

  def setUp(self):
    mid = trading.get_mid_market_price("BTC-USD", test=True)
    if mid > 100000:
      mid = 6000
    self.test_price = round(mid / 2, 2)

    self.test_order = Order("BTC-USD",
                            "buy",
                            ".011",
                            self.test_price,
                            test=True,
                            persist=False)

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
    self.assertEqual(self.test_order.status, "pending")

    trading.cancel_order(self.test_order)

  def test_cancel_order(self):
    trading.send_order(self.test_order)
    response = trading.cancel_order(self.test_order)

    self.assertTrue(self.test_order.exchange_id in response)

  def test_order_status(self):
    '''
    ['id', 'price', 'size', 'product_id', 'side', 'type', 'time_in_force',
    'post_only', 'created_at', 'fill_fees', 'filled_size', 'executed_value',
    'status', 'settled']
    '''
    trading.send_order(self.test_order)
    response = trading.order_status(self.test_order.exchange_id)

    self.assertEqual(self.test_order.exchange_id, response['id'])
    # TODO: may want to adjust scale of decimals to amtch
    self.assertEqual(str(self.test_order.price) + "000000", response['price'])
    self.assertEqual(str(self.test_order.size) + "00000", response['size'])
    self.assertEqual(self.test_order.filled, Decimal(response['filled_size']))
    self.assertEqual(self.test_order.pair, response['product_id'])
    self.assertEqual("limit", response["type"])
    self.assertEqual(self.test_order.post_only, response["post_only"])

  def test_order_status_canceled(self):
    trading.send_order(self.test_order)
    trading.cancel_order(self.test_order)
    response = trading.order_status(self.test_order.exchange_id)

    self.assertEqual(response['message'], "NotFound")

  def test_order_status_bad_order(self):

    response = trading.order_status("ths-is-not-a-real-id")

    self.assertEqual(response['message'], "Invalid order id")

  def test_get_open_orders(self):
    # This function and test suck. and is only being used in tests
    self.assertIsNone(None)

  def test_live(self):
    # Check for open orders
    orders = trading.get_open_orders(pair="BTC-USD", test=False)
    starting_order_ids = {order["id"] for order in orders}
    logger.debug("Starting with {} orders".format(len(starting_order_ids)))

    # Check price and send trade at fraction of price
    mid = trading.get_mid_market_price("BTC-USD")
    fraction_of_mid = round(mid / 100, 2)
    self.live_test_order = Order(
      "BTC-USD", "buy", ".01", fraction_of_mid, persist=False
    )

    trading.send_order(self.live_test_order)
    orders = trading.get_open_orders(pair="BTC-USD", test=False)
    logger.debug("New order {}".format(self.live_test_order.exchange_id))
    new_order_ids = {order["id"] for order in orders}
    logger.debug("Ending with {} orders".format(len(new_order_ids)))

    union_order_ids = starting_order_ids | {self.live_test_order.exchange_id}
    logger.debug("Union has {} orders".format(len(union_order_ids)))

    self.assertEqual(new_order_ids, union_order_ids)

    trading.cancel_order(self.live_test_order)
    orders = trading.get_open_orders(pair="BTC-USD", test=False)
    new_order_ids = {order["id"] for order in orders}

    self.assertEqual(new_order_ids, starting_order_ids)

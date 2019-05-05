import unittest
import logging.config
from decimal import Decimal

import config
from trader.exchange.order import Order
from trader.exchange.api_wrapper.coinbase_pro import CoinbasePro

CPTrading = CoinbasePro(test=True)

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class test_coinbase_pro_trading(unittest.TestCase):

  def setUp(self):
    mid = CPTrading.get_mid_market_price("BTC-USD")
    if mid > 100000:
      mid = 6000
    self.test_price = round(mid / 2, 2)

    self.test_order = Order("BTC-USD",
                            "buy",
                            ".011",
                            self.test_price,
                           )

  def test_send_order(self):
    CPTrading.send_order(self.test_order)
    response = self.test_order.response

    self.assertEqual(response["side"], "buy")
    self.assertEqual(response["post_only"], True)
    self.assertEqual(response["type"], "limit")
    self.assertEqual(response["size"], "{:.8f}".format(0.011))
    self.assertEqual(response["price"], "{:.8f}".format(self.test_price))
    self.assertEqual(response["product_id"], "BTC-USD")
    self.assertEqual(response["status"], "pending")
    self.assertEqual(self.test_order.status, "pending")

    CPTrading.cancel_order(self.test_order)

  def test_cancel_order(self):
    CPTrading.send_order(self.test_order)
    response = CPTrading.cancel_order(self.test_order)

    self.assertTrue(self.test_order.exchange_id in response)

  def test_order_status(self):
    '''
    ['id', 'price', 'size', 'product_id', 'side', 'type', 'time_in_force',
    'post_only', 'created_at', 'fill_fees', 'filled_size', 'executed_value',
    'status', 'settled']
    '''
    CPTrading.send_order(self.test_order)
    response = CPTrading.order_status(self.test_order.exchange_id)

    self.assertEqual(self.test_order.exchange_id, response['id'])
    # TODO: may want to adjust scale of decimals to match
    self.assertEqual(str(self.test_order.price) + "000000", response['price'])
    self.assertEqual(str(self.test_order.size) + "00000", response['size'])
    self.assertEqual(self.test_order.filled, Decimal(response['filled_size']))
    self.assertEqual(self.test_order.pair, response['product_id'])
    self.assertEqual("limit", response["type"])
    self.assertEqual(self.test_order.post_only, response["post_only"])

  def test_order_status_canceled(self):
    CPTrading.send_order(self.test_order)
    CPTrading.cancel_order(self.test_order)
    response = CPTrading.order_status(self.test_order.exchange_id)

    self.assertEqual(response['message'], "NotFound")

  def test_order_status_bad_order(self):

    response = CPTrading.order_status("ths-is-not-a-real-id")

    self.assertEqual(response['message'], "Invalid order id")

  def test_get_open_orders(self):
    # This function and test suck. and is only being used in tests
    self.assertIsNone(None)

  def test_live(self):
    # Check price and send trade at fraction of price
    mid = CPTrading.get_mid_market_price("BTC-USD")
    fraction_of_mid = round(mid / 100, 2)

    live_test_order = Order(
      "BTC-USD", "buy", ".01", fraction_of_mid
    )

    # Send order and check
    CPTrading.send_order(live_test_order)
    print("id {}".format(live_test_order.exchange_id))
    check_order = CPTrading.order_status(live_test_order.exchange_id)
    logger.debug(check_order)

    # Cancel order and check
    CPTrading.cancel_order(live_test_order)
    check_canceled_order = CPTrading.order_status(live_test_order.exchange_id)
    logger.debug(check_canceled_order)

    self.assertEqual(check_order['id'], live_test_order.exchange_id)
    self.assertEqual(check_order['price'], str(fraction_of_mid) + '000000')
    self.assertEqual(check_order['size'], "0.01000000")
    self.assertEqual(check_order['product_id'], 'BTC-USD')
    self.assertEqual(check_order['side'], 'buy')
    self.assertEqual(check_order['type'], 'limit')
    self.assertEqual(check_order['time_in_force'], 'GTC')
    self.assertEqual(check_order['post_only'], True)
    self.assertEqual(check_order['fill_fees'], '0.0000000000000000')
    self.assertEqual(check_order['filled_size'], '0.00000000')
    self.assertEqual(check_order['executed_value'], '0.0000000000000000')
    self.assertEqual(check_order['status'], 'open')
    self.assertEqual(check_order['settled'], False)
    self.assertEqual(check_canceled_order['message'], 'NotFound')

from ..exchange import order
from ..exchange import trading
import unittest


class test_trading(unittest.TestCase):

  def set_up(self):
    mid = trading.get_mid_market_price("BTC-USD", test=True)
    self.test_price = round(mid - 3.14, 2)

    self.test_order = order.Order("BTC-USD",
                                  "buy",
                                  .05,
                                  self.test_price,
                                  test=True)

  def test_send_order(self):
    self.set_up()
    trading.send_order(self.test_order)
    response = self.test_order.responses[0]

    self.assertEqual(response["side"], "buy")
    self.assertEqual(response["post_only"], True)
    self.assertEqual(response["type"], "limit")
    self.assertEqual(response["size"], "0.05000000")
    self.assertEqual(response["price"], str(self.test_price) + "000000")
    self.assertEqual(response["product_id"], "BTC-USD")
    self.assertEqual(response["status"], "pending")
    self.assertEqual(self.test_order.history[0]["status"], "Created")
    self.assertEqual(self.test_order.history[1]["status"], "pending")

    trading.cancel_order(self.test_order)

  def test_cancel_order(self):
    self.set_up()
    trading.send_order(self.test_order)
    trading.cancel_order(self.test_order)
    response = self.test_order.responses[1]

    self.assertTrue(self.test_order.id not in response)

  def test_get_open_orders(self):
    self.set_up()
    orders = trading.get_open_orders(test=True)
    starting_order_ids = {order["id"] for order in orders}

    trading.send_order(self.test_order)
    orders = trading.get_open_orders(test=True)
    new_order_ids = {order["id"] for order in orders}

    union_order_ids = starting_order_ids | {self.test_order.id}

    self.assertEqual(new_order_ids, union_order_ids)

    trading.cancel_order(self.test_order)
    orders = trading.get_open_orders(test=True)
    new_order_ids = {order["id"] for order in orders}

    self.assertEqual(new_order_ids, starting_order_ids)

from ..exchange import order
from ..exchange import trading
import unittest

# Name                                Stmts   Miss  Cover   Missing
# -----------------------------------------------------------------
# trader/exchange/trading.py             63      1    98%   67


class test_trading(unittest.TestCase):

  def setUp(self):
    mid = trading.get_mid_market_price("BTC-USD", test=True)
    if mid > 100000:
      mid = 6000
    self.test_price = round(mid*.5, 2)

    self.test_order = order.Order("BTC-USD",
                                  "buy",
                                  .011,
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
    print("Starting with {} orders".format(len(starting_order_ids)))

    trading.send_order(self.test_order)
    orders = trading.get_open_orders(pair="BTC-USD", test=True)
    print("New order {}".format(self.test_order.id))
    new_order_ids = {order["id"] for order in orders}
    print("Ending with {} orders".format(len(new_order_ids)))

    union_order_ids = starting_order_ids | {self.test_order.id}
    print("Union has {} orders".format(len(union_order_ids)))

    self.assertEqual(new_order_ids, union_order_ids)

    trading.cancel_order(self.test_order)
    orders = trading.get_open_orders(pair="BTC-USD", test=True)
    new_order_ids = {order["id"] for order in orders}

    self.assertEqual(new_order_ids, starting_order_ids)

  def test_live(self):
    mid = trading.get_mid_market_price("BTC-USD")
    half_mid = round(mid / 100, 2)
    self.live_test_order = order.Order("BTC-USD", "buy", .01, half_mid)
    orders = trading.get_open_orders(pair="BTC-USD")
    starting_order_ids = {order["id"] for order in orders}
    print("Starting with {} orders".format(len(starting_order_ids)))

    trading.send_order(self.live_test_order)
    orders = trading.get_open_orders(pair="BTC-USD")
    print("New order {}".format(self.live_test_order.id))
    new_order_ids = {order["id"] for order in orders}
    print("Ending with {} orders".format(len(new_order_ids)))

    union_order_ids = starting_order_ids | {self.live_test_order.id}
    print("Union has {} orders".format(len(union_order_ids)))

    self.assertEqual(new_order_ids, union_order_ids)

    trading.cancel_order(self.live_test_order)
    orders = trading.get_open_orders(pair="BTC-USD")
    new_order_ids = {order["id"] for order in orders}

    self.assertEqual(new_order_ids, starting_order_ids)

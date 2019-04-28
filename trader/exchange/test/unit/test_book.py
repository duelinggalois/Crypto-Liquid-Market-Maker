import unittest
from decimal import Decimal

from ...book import Book
from ... import trading


class Test_Book(unittest.TestCase):
  def setUp(self):
    self.book = Book("BTC-USD", persist=False, test=True)
    self.market_price = trading.get_mid_market_price("BTC-USD", test=True)
    self.details = trading.get_product("BTC-USD", test=True)

  def test_book_init(self):

    self.assertEqual(self.book.pair, "BTC-USD")
    self.assertEqual(self.book.ready_orders, [])
    self.assertEqual(self.book.open_orders, [])
    self.assertEqual(self.book.filled_orders, [])
    self.assertEqual(self.book.canceled_orders, [])

  def test_book_add_order(self):
    price = round(-1 + self.market_price, 2)
    self.book.add_order("buy", ".1", price)

    self.assertEqual(len(self.book.ready_orders), 1)

    order = self.book.ready_orders[0]
    self.assertEqual(order.price, price)
    self.assertEqual(order.pair, "BTC-USD")
    self.assertEqual(order.size, Decimal(".1"))
    self.assertEqual(order.side, "buy")

    price = round(-1 + self.market_price, 2)
    self.book.add_order("sell", ".11", price)

    self.assertEqual(len(self.book.ready_orders), 2)
    order = self.book.ready_orders[1]
    self.assertEqual(order.price, price)
    self.assertEqual(order.pair, "BTC-USD")
    self.assertEqual(order.size, Decimal(".11"))
    self.assertEqual(order.side, "sell")

  def test_book_send_orders(self):
    price = round(1 + self.market_price, 2)
    self.book.add_order("sell", ".11", price)
    self.book.send_orders()

    self.assertEqual(self.book.ready_orders, [])
    self.assertEqual(len(self.book.open_orders), 1)

    send_id = self.book.open_orders[0].exchange_id
    sent_ids = self.get_ids()

    self.assertTrue(send_id in sent_ids)

    self.book.add_order("buy", ".1", self.market_price - 1)
    self.book.add_order("sell", ".2", self.market_price + 2)
    self.book.send_orders()

    self.assertEqual(self.book.ready_orders, [])
    self.assertEqual(len(self.book.open_orders), 3)

    book_ids = {order.exchange_id for order in self.book.open_orders}
    sent_ids = self.get_ids()
    sent_ids = {ids for ids in sent_ids if ids in book_ids}

    self.assertEqual(book_ids, sent_ids)

    self.book.cancel_all_orders()
    self.assertEqual(self.book.open_orders, [])
    self.assertEqual(len(self.book.canceled_orders), 3)

    canceled_ids = book_ids
    sent_ids = {ids for ids in self.get_ids()}
    self.assertEqual(canceled_ids & sent_ids, set())

  def test_order_filled(self):
    price = round(self.market_price + 1, 2)
    self.book.add_order("sell", ".11", price)
    self.book.send_orders()
    order = self.book.open_orders[0]

    # Tell book, order is filled
    self.book.order_filled(order)

    self.assertEqual(self.book.open_orders, [])
    self.assertEqual(len(self.book.filled_orders), 1)

    filled_order = self.book.filled_orders[0]

    self.assertEqual(order.exchange_id, filled_order.exchange_id)

    # move order back to open and cancel it.
    self.book.open_orders = [filled_order]
    self.book.cancel_all_orders()

  def test_add_send_order(self):
    side = "buy"
    size = self.details['base_min_size']
    price = self.market_price / Decimal("10")
    self.book.add_and_send_order(
      side, size, price)

    self.assertEqual(len(self.book.open_orders), 1,
                     msg="Order should be in open orders")
    self.assertEqual(len(self.book.ready_orders), 0,
                     msg="Nothing should be in ready_orders")
    test_order = self.book.open_orders[0]

    self.assertEqual(test_order.status, "open",
                     msg="Status will be open")
    trading.cancel_order(test_order)
    self.assertEqual(test_order.status, "canceled",
                     msg="failed to cancel order for test")

  def test_add_send_order_no_post_only(self):
    size = self.details['base_min_size']
    side = "buy"
    price = self.market_price * Decimal("5")
    self.book.add_and_send_order(side, size, price, post_only=False)

    self.assertEqual(len(self.book.filled_orders), 1)
    self.assertEqual(len(self.book.open_orders), 0)
    self.assertEqual(self.book.filled_orders[0].status, "filled")

  def test_add_send_order_post_only(self):
    size = self.details['base_min_size']
    side = "buy"
    price = self.market_price * Decimal("5")
    self.book.add_and_send_order(side, size, price, post_only=True)

    self.assertEqual(len(self.book.open_orders), 0,
                     msg="Order should be rejected not open")
    self.assertEqual(len(self.book.canceled_orders), 0,
                     msg="Order should be rejected not canceled")
    self.assertEqual(len(self.book.rejected_orders), 1,
                     msg=("Post only order that would fill was not rejected"))

  def get_ids(self):
    return [order["id"] for order in trading
            .get_open_orders(pair="BTC-USD", test=True)]

import unittest
from decimal import Decimal

from ...book import Book
from ... import trading


class Test_Book(unittest.TestCase):
  def setUp(self):
    self.book = Book("LTC-USD", persist=False, test=True)
    self.market_price = trading.get_mid_market_price("LTC-USD", test=True)

  def test_book_init(self):

    self.assertEqual(self.book.pair, "LTC-USD")
    self.assertEqual(self.book.unsent_orders, [])
    self.assertEqual(self.book.open_orders, [])
    self.assertEqual(self.book.filled_orders, [])
    self.assertEqual(self.book.canceled_orders, [])

  def test_book_add_order(self):
    price = round(-1 + self.market_price, 2)
    self.book.add_order("buy", ".1", price)

    self.assertEqual(len(self.book.unsent_orders), 1)

    order = self.book.unsent_orders[0]
    self.assertEqual(order.price, price)
    self.assertEqual(order.pair, "LTC-USD")
    self.assertEqual(order.size, Decimal(".1"))
    self.assertEqual(order.side, "buy")

    price = round(-1 + self.market_price, 2)
    self.book.add_order("sell", ".11", price)

    self.assertEqual(len(self.book.unsent_orders), 2)
    order = self.book.unsent_orders[1]
    self.assertEqual(order.price, price)
    self.assertEqual(order.pair, "LTC-USD")
    self.assertEqual(order.size, Decimal(".11"))
    self.assertEqual(order.side, "sell")

  def test_book_send_orders(self):
    price = round(1 + self.market_price, 2)
    self.book.add_order("sell", ".11", price)
    self.book.send_orders()

    self.assertEqual(self.book.unsent_orders, [])
    self.assertEqual(len(self.book.open_orders), 1)

    send_id = self.book.open_orders[0].exchange_id
    sent_ids = self.get_ids()

    self.assertTrue(send_id in sent_ids)

    self.book.add_order("buy", ".1", self.market_price - 1)
    self.book.add_order("sell", ".2", self.market_price + 2)
    self.book.send_orders()

    self.assertEqual(self.book.unsent_orders, [])
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
    order_id = self.book.open_orders[0].exchange_id

    # Tell book, order is filled
    self.book.order_filled(order_id)

    self.assertEqual(self.book.open_orders, [])
    self.assertEqual(len(self.book.filled_orders), 1)

    filled_order = self.book.filled_orders[0]

    self.assertEqual(order_id, filled_order.exchange_id)

    # move order back to open and cancel it.
    self.book.open_orders = [filled_order]
    self.book.cancel_all_orders()

  def get_ids(self):
    return [order["id"] for order in trading
            .get_open_orders(pair="LTC-USD", test=True)]

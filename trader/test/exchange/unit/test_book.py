# Commented out these tests after refactor of Book to load
# from database in persisted book.


# import unittest
# from decimal import Decimal
# from unittest.mock import patch

# from trader.exchange.persisted_book import Book
# from trader.exchange import trading
# from trader.test import resources


# class Test_Book(unittest.TestCase):

#   def setUp(self):
    
#     self.book = Book("BTC-USD", test=True)
#     self.market_price = Decimal("555.55")
#     self.details = resources.btc_usd_product_return

  # def test_book_init(self):

  #   self.assertEqual(self.book.pair, "BTC-USD")
  #   self.assertEqual(self.book.ready_orders(), [])
  #   self.assertEqual(self.book.open_orders(), [])
  #   self.assertEqual(self.book.filled_orders(), [])
  #   self.assertEqual(self.book.canceled_orders(), [])

  # def test_book_add_order(self):
  #   price = round(-1 + self.market_price, 2)
  #   self.book.add_order("buy", ".1", price)

  #   self.assertEqual(len(self.book.ready_orders()), 1)

  #   order = self.book.ready_orders[0]
  #   self.assertEqual(order.price, price)
  #   self.assertEqual(order.pair, "BTC-USD")
  #   self.assertEqual(order.size, Decimal(".1"))
  #   self.assertEqual(order.side, "buy")

  #   price = round(-1 + self.market_price, 2)
  #   self.book.add_order("sell", ".11", price)

  #   self.assertEqual(len(self.book.ready_orders), 2)
  #   order = self.book.ready_orders[1]
  #   self.assertEqual(order.price, price)
  #   self.assertEqual(order.pair, "BTC-USD")
  #   self.assertEqual(order.size, Decimal(".11"))
  #   self.assertEqual(order.side, "sell")

  # def test_book_send_orders(self):
  #   price = round(1 + self.market_price, 2)
  #   self.book.add_order("sell", ".11", price)
  #   self.book.send_orders()

  #   self.assertEqual(self.book.ready_orders, [])
  #   self.assertEqual(len(self.book.open_orders), 1)

  #   send_id = self.book.open_orders[0].exchange_id
  #   sent_ids = self.get_ids()

  #   self.assertTrue(send_id in sent_ids)

  #   self.book.add_order("buy", ".1", self.market_price - 1)
  #   self.book.add_order("sell", ".2", self.market_price + 2)
  #   self.book.send_orders()

  #   self.assertEqual(self.book.ready_orders, [])
  #   self.assertEqual(len(self.book.open_orders), 3)

  #   book_ids = {order.exchange_id for order in self.book.open_orders}
  #   sent_ids = self.get_ids()
  #   sent_ids = {ids for ids in sent_ids if ids in book_ids}

  #   self.assertEqual(book_ids, sent_ids)

  #   self.book.cancel_all_orders()
  #   self.assertEqual(self.book.open_orders, [])
  #   self.assertEqual(len(self.book.canceled_orders), 3)

  #   canceled_ids = book_ids
  #   sent_ids = {ids for ids in self.get_ids()}
  #   self.assertEqual(canceled_ids & sent_ids, set())

  # def test_order_filled(self):
  #   price = round(self.market_price + 1, 2)
  #   self.book.add_order("sell", ".11", price)
  #   self.book.send_orders()
  #   order = self.book.open_orders[0]

  #   # Tell book, order is filled
  #   self.book.order_filled(order)

  #   self.assertEqual(self.book.open_orders, [])
  #   self.assertEqual(len(self.book.filled_orders), 1)

  #   filled_order = self.book.filled_orders[0]

  #   self.assertEqual(order.exchange_id, filled_order.exchange_id)

  #   # move order back to open and cancel it.
  #   self.book.open_orders = [filled_order]
  #   self.book.cancel_all_orders()

  # def test_add_send_order(self):
  #   side = "buy"
  #   size = self.details['base_min_size']
  #   price = self.market_price / Decimal("10")
  #   self.book.add_and_send_order(
  #     side, size, price)

  #   self.assertEqual(len(self.book.open_orders), 1,
  #                    msg="Order should be in open orders")
  #   self.assertEqual(len(self.book.ready_orders), 0,
  #                    msg="Nothing should be in ready_orders")
  #   test_order = self.book.open_orders[0]

  #   self.assertEqual(test_order.status, "open",
  #                    msg="Status will be open")
  #   trading.cancel_order(test_order)
  #   self.assertEqual(test_order.status, "canceled",
  #                    msg="failed to cancel order for test")

  # def test_add_send_order_no_post_only(self):
  #   size = self.details['base_min_size']
  #   side = "buy"
  #   price = self.market_price * Decimal("5")
  #   self.book.add_and_send_order(side, size, price, post_only=False)

  #   self.assertEqual(len(self.book.filled_orders), 1)
  #   self.assertEqual(len(self.book.open_orders), 0)
  #   self.assertEqual(self.book.filled_orders[0].status, "filled")

  # def test_add_send_order_post_only(self):
  #   size = self.details['base_min_size']
  #   side = "buy"
  #   price = self.market_price * Decimal("5")
  #   self.book.add_and_send_order(side, size, price, post_only=True)

  #   self.assertEqual(len(self.book.canceled_orders), 0,
  #                    msg="Order should be rejected not canceled")
  #   self.assertEqual(len(self.book.open_orders), 1,
  #                    msg="Order should still post")
  #   order_to_cancel = self.book.open_orders[0]
  #   trading.cancel_order(order_to_cancel)
  #   self.assertGreater(len(self.book.rejected_orders), 0,
  #                      msg=("rejects could be should be one or more with order"
  #                           " changes after polling"))
  #   self.assertEqual(self.book.rejected_orders[0].reject_reason, "post only")
  #   self.assertEqual(order_to_cancel.status, "canceled")

  # def test_cancel_order_by_attribute(self):
  #   side = "buy"
  #   size = ".1"
  #   price1 = self.market_price / 2
  #   price2 = self.market_price * 2 / 3
  #   self.book.add_and_send_order(side, size, price1)
  #   self.assertEqual(len(self.book.open_orders), 1,
  #                    msg="One open order in book")
  #   order1 = self.book.open_orders[0]
  #   self.book.add_and_send_order(side, size, price2)
  #   self.assertEqual(len(self.book.open_orders), 2,
  #                    msg="Two open orders in book")
  #   order2 = next(o for o in self.book.open_orders if o != order1)
  #   self.book.cancel_order_by_attribute(side, Decimal(size))
  #   self.assertEqual(len(self.book.open_orders), 1,
  #                    msg="One open order in book")
  #   self.assertEqual(len(self.book.canceled_orders), 1,
  #                    msg="One open order in book")
  #   open_order = self.book.open_orders[0]
  #   canceled_order = self.book.canceled_orders[0]

  #   self.assertEqual(open_order, order2,
  #                    msg="Second posted order should not be canceled")
  #   self.assertEqual(canceled_order, order1,
  #                    msg="First posted order should be canceled")

  # def get_ids(self):
  #   return [order["id"] for order in trading
  #           .get_open_orders(pair="BTC-USD", test=True)]


# def test_send_order_rejected(self, mock_send_order, mock_confirm_order,
  #                              mock_get_product, mock_get_first_book):
  #   """Post only orders are the default and will be rejected with extreme
  #   price movement, this test checks that order will be adjusted until it
  #   is posted.
  #   """
  #
  #   size = "1.233"
  #   side = "buy"
  #   book = self.session.query(Book).filter(Book.id == self.book_id).one()
  #   buy_order = book.add_order(side, size, "105.05")
  #   book.send_order(buy_order)
  #
  #   self.assertEqual(len(book.get_open_orders()), 1)
  #   open_order_0 = book.get_open_orders()[0]
  #   self.assertEqual(open_order_0.price, Decimal("99.99"))
  #   self.assertEqual(open_order_0.size, Decimal(size))
  #   self.assertEqual(open_order_0.side, side)
  #   persisted_book.trading.confirm_order.assert_called_once_with(open_order_0)
  #
  #   self.assertEqual(len(book.get_rejected_orders()), 3)
  #   rejected_0 = book.get_rejected_orders()[0]
  #   rejected_1 = book.get_rejected_orders()[1]
  #   rejected_2 = book.get_rejected_orders()[2]
  #   self.assertEqual(rejected_0, buy_order)
  #   self.assertEqual(rejected_0.price, Decimal("105.05"))
  #   self.assertEqual(rejected_0.size, Decimal(size))
  #   self.assertEqual(rejected_0.side, side)
  #
  #   self.assertEqual(rejected_1.price, Decimal("102.22"))
  #   self.assertEqual(rejected_1.size, Decimal(size))
  #   self.assertEqual(rejected_1.side, side)
  #
  #   self.assertEqual(rejected_2.price, Decimal("101.12"))
  #   self.assertEqual(rejected_2.size, Decimal(size))
  #   self.assertEqual(rejected_2.side, side)
  #
  #   side = "sell"
  #   size = "0.001"
  #   sell_order = book.add_order(side, size, "75.05")
  #   book.send_order(sell_order)
  #
  #   self.assertEqual(len(book.get_open_orders()), 2)
  #   open_order_1 = book.get_open_orders()[1]
  #   self.assertEqual(open_order_1.price, Decimal("99"))
  #   self.assertEqual(open_order_1.size, Decimal(size))
  #   self.assertEqual(open_order_1.side, side)
  #
  #   self.assertEqual(len(book.get_rejected_orders()), 6)
  #   rejected_3 = book.get_rejected_orders()[3]
  #   rejected_4 = book.get_rejected_orders()[4]
  #   rejected_5 = book.get_rejected_orders()[5]
  #   self.assertEqual(rejected_3, sell_order)
  #   self.assertEqual(rejected_3.price, Decimal("75.05"))
  #   self.assertEqual(rejected_3.size, Decimal(size))
  #   self.assertEqual(rejected_3.side, side)
  #
  #   self.assertEqual(rejected_4.price, Decimal("95.35"))
  #   self.assertEqual(rejected_4.size, Decimal(size))
  #   self.assertEqual(rejected_4.side, side)
  #
  #   self.assertEqual(rejected_5.price, Decimal("98.99"))
  #   self.assertEqual(rejected_5.size, Decimal(size))
  #   self.assertEqual(rejected_5.side, side)
  #   logger.error(persisted_book.trading.send_order.called)
  #
  #   mock_send_order.assert_has_calls([
  #     call(rejected_0), call(rejected_1), call(rejected_2), call(open_order_0),
  #     call(rejected_3), call(rejected_4), call(rejected_5), call(open_order_1)
  #   ])
  #   persisted_book.trading.confirm_order.assert_has_calls([
  #     call(open_order_0), call(open_order_1)
  #   ])

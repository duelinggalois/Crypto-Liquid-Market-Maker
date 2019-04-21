import unittest

from ...book import Book
from ....database.manager import (
  BaseWrapper, Test_Engine, test_session, get_order_from_db)


class Test_Order_Integration(unittest.TestCase):

  def setUp(self):
    self.book = Book("BTC-USD", test=True, persist=False)

  def tearDown(self):
    self.book.cancel_all_orders()
    test_session.close()
    BaseWrapper.metadata.drop_all(Test_Engine)

  def test_init(self):
    self.book.add_order("buy", 1, 1)
    order = self.book.ready_orders[0]
    order.save()
    order.session.commit()

    order_in_db = get_order_from_db(
      order.id, test=True
    )

    self.assertIsNotNone(order_in_db)
    self.assertEqual(order_in_db[0], order.id)

import logging
import logging.config
import unittest

import config
from ...order import Order
from ... import trading
from trader.database.manager import (
  get_order_from_db, BaseWrapper, Test_Engine, test_session
)


logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class Test_Order_Integration(unittest.TestCase):

  def setUp(self):
    mm = trading.get_mid_market_price("BTC-USD", test=True)
    BaseWrapper.metadata.create_all(Test_Engine)
    self.test_order = Order("BTC-USD", "buy", 1, mm / 2, test=True)

  def tearDown(self):
    test_session.close()
    BaseWrapper.metadata.drop_all(Test_Engine)

  def test_order_id(self):
    # No id will be assigned until saved
    self.assertIsNone(self.test_order.id)

    self.test_order.save()
    self.assertIsNotNone(self.test_order.id)

    pre_commit = get_order_from_db(
      self.test_order.id, test=True
    )
    self.assertIsNone(pre_commit)

    self.test_order.session.commit()
    commited = get_order_from_db(
      self.test_order.id, test=True
    )

    self.assertEqual(commited[0], self.test_order.id)

  def test_columns(self):
    self.test_order.save()
    self.test_order.session.commit()

    order_in_db = get_order_from_db(
      self.test_order.id, test=True
    )
    self.assertEqual(order_in_db[1], self.test_order.created_at)
    # TODO: Issue 35 change or create get_order_from_db to return a dictionary
    # Exchange does not exist until sent
    self.assertIsNone(order_in_db[2])
    self.assertIsNone(order_in_db[3])
    self.assertIsNone(self.test_order.exchange_id)
    self.assertIsNone(self.test_order.book_id)
    self.assertEqual(order_in_db[4], self.test_order.pair)
    self.assertEqual(order_in_db[5], self.test_order.side)
    self.assertEqual(order_in_db[6], self.test_order.price)
    self.assertEqual(order_in_db[7], self.test_order.size)
    self.assertEqual(order_in_db[8], self.test_order.filled)
    self.assertEqual(order_in_db[9], self.test_order.status)
    self.assertEqual(order_in_db[10], self.test_order.post_only)
    self.assertEqual(order_in_db[11], self.test_order.test)

  def test_send(self):

    self.test_order.save()
    self.test_order.session.commit()
    pre_sent_db = get_order_from_db(
      self.test_order.id, test=True
    )
    trading.send_order(self.test_order)

    self.test_order.session.commit()
    sent_db = get_order_from_db(
      self.test_order.id, test=True
    )

    self.assertIsNone(pre_sent_db[2])
    self.assertIsNotNone(sent_db[2])
    self.assertEqual(sent_db[9], "pending")
    self.assertEqual(self.test_order.status, "pending")

    for i in (0, 1, 3, 4, 5, 6, 7, 10, 11):
      logger.debug("Testing column {}.".format(i))
      self.assertEqual(pre_sent_db[i], sent_db[i])

  def test_cancel(self):

    self.test_order.save()
    trading.send_order(self.test_order)
    trading.cancel_order(self.test_order)
    self.test_order.session.commit()
    order_in_db = get_order_from_db(
      self.test_order.id, test=True
    )
    self.assertEqual(order_in_db[9], "canceled")
    self.assertEqual(self.test_order.status, "canceled")

  def test_delete(self):

    self.test_order.save()
    self.test_order.delete()
    self.test_order.session.commit()

    deleted = get_order_from_db(
      self.test_order.id, test=True
    )

    self.assertIsNone(deleted)

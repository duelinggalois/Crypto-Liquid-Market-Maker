import logging
import logging.config
import unittest

import config
from trader.exchange.order import Order
from trader.database.db import dal

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class TestOrdeIntegration(unittest.TestCase):

  def setUp(self):

    dal.connect(test=True)
    self.connection = dal.engine.connect()
    self.trans = self.connection.begin()
    self.session = dal.Session(bind=self.connection)
    self.prep_db()

  def tearDown(self):
    self.session.close()
    self.trans.rollback()
    self.connection.close()
    dal.Session.close_all()

  def test_get_order(self):
    order = self.session.query(Order).filter(Order.id == self.order_id).one()
    self.assertIsNotNone(order)
    self.assertEqual(order.pair, "BTC-USD")
    self.assertEqual(order.side, "buy")
    self.assertEqual(order.size, 1)
    self.assertEqual(order.filled, 0)
    self.assertEqual(order.status, "ready")
    self.assertEqual(order.post_only, True)
    # Populated when sent to exchange.
    self.assertIsNone(order.exchange_id)
    # Not in metadata model currently
    # self.assertIsNone(order.history)
    # self.assertIsNone(order.responses)
    # self.assertEqual(order.persist, True)

  def test_delete(self):
    order = self.session.query(Order).filter(Order.id == self.order_id).one()
    self.session.delete(order)
    self.session.commit()
    deleted_order_query = self.session.query(Order).filter(
      Order.id == self.order_id
    )
    self.assertEqual(deleted_order_query.count(), 0,
                     msg="Order was deleted and can not be queried for")

  def prep_db(self):
    order = Order("BTC-USD", "buy", 1, "250")
    self.session.add(order)
    self.session.commit()
    self.order_id = order.id

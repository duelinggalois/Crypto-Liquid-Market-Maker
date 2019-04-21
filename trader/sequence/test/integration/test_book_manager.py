import logging
import logging.config
import unittest

import config
from ...book_manager import BookManager
from ...trading_terms import TradingTerms
from trader.exchange import trading
from trader.database.manager import (
  BaseWrapper, test_session, Test_Engine, get_order_from_db
)


logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class TestBookManagerIntegration(unittest.TestCase):

  def setUp(self):
    mid_price = trading.get_mid_market_price(
      "BTC-USD", test=True
    )
    low_price = mid_price / 5
    budget = mid_price * 3
    self.terms = TradingTerms(
      "BTC-USD", budget, ".01", ".015", low_price
    )
    self.book_manager = BookManager(self.terms)

  def tearDown(self):
    self.book_manager.book.cancel_all_orders()
    test_session.close()
    BaseWrapper.metadata.drop_all(Test_Engine)

  def test_init(self):
    for order in self.book_manager.book.ready_orders:
      if logger.isEnabledFor(logging.DEBUG):
        count = len(self.book_manager.book.ready_orders)
        logger.debug(
          "Verifying ready order number {} of {}".format(
            self.book_manager.book.ready_orders.index(order) + 1,
            count
          )
        )
      order_in_db = get_order_from_db(
        order.id, test=True
      )
      self.assertEqual(order_in_db[0], order.id)
      self.assertIsNone(order.exchange_id)
      self.assertIsNone(order_in_db[2])
      self.assertEqual(order_in_db[9], "ready")

  def test_send_order(self):
    self.book_manager.send_orders()
    for order in self.book_manager.book.open_orders:
      if logger.isEnabledFor(logging.DEBUG):
        count = len(self.book_manager.book.open_orders)
        logger.debug(
          "Verifying open order number {} of {}".format(
            self.book_manager.book.open_orders.index(
              order) + 1,
            count
          )
        )
      order_in_db = get_order_from_db(
        order.id, test=True
      )
      self.assertEqual(order_in_db[0], order.id)
      self.assertIsNotNone(order_in_db[2])
      self.assertEqual(order_in_db[2], order.exchange_id)
      self.assertEqual(order_in_db[9], "open")

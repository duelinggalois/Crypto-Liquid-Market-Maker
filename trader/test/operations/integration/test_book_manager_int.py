from decimal import Decimal
import logging
import logging.config
import unittest

import config
from trader.database.db import dal
from trader.exchange.api_enum import ApiEnum
from trader.exchange.api_provider import ApiProvider
from trader.database.models.order import Order
from trader.database.models.book import Book
from trader.operations.book_manager import book_manager_maker
from trader.database.models import trading_terms

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class TestBookManagerIntegration(unittest.TestCase):

  def setUp(self):
    """Test case set up
    | price | size | value |
    |  1500 |  5.5 |  5500 |
    |  1400 |  4.5 |  4500 |
    |  1300 |  3.5 |  3500 |
    |  1200 |  2.5 |  2500 |
    |  1100 |  1.5 |  1500 |
    |  1000 |  0   |     0 |
    |   900 |  1.0 |   900 |
    |   800 |  2.0 |  1600 |
    |   700 |  3.0 |  2100 |
    |   600 |  4.0 |  2400 |
    |   500 |  5.0 |  2500 |
         | sbtotal | 27000 |
         | fee     |    81 |
         | total   | 27081 |

    """
    dal.connect(test=True)
    self.session = dal.Session()

    low_price = Decimal("500")
    budget = Decimal("27000") * (1 + Decimal(config.CB_FEE))
    noop_api = ApiProvider.noop_api
    noop_api.pairs = ["BTC-USD"]
    noop_api.mid_market_prices=["1000"]
    self.terms = trading_terms.TradingTermsBase(
      "BTC-USD", budget, "1", ".5", low_price, api_enum=ApiEnum.NoopApi)

    self.BookManagerMaker = book_manager_maker(self.terms,
                                               trading_api=noop_api)
    self.book_manager = self.BookManagerMaker()

  def tearDown(self):
    ApiProvider.noop_api.reset_noop()
    self.session.query(Order).filter(
      Order.book_id == self.book_manager.book_id).delete()
    self.session.query(Book).filter(
      Book.id == self.book_manager.book_id).delete()
    self.session.commit()
    self.session.close()
    self.session.close_all()

  def test_init(self):
    book = self.session.query(Book).filter(
      Book.id == self.book_manager.book_id
    ).one()
    orders = book.get_ready_orders()
    self.assertEqual(len(orders), 10)
    for order in orders:
      self.assertIsNone(order.exchange_id)

  def test_send_order(self):
    self.book_manager.load_book()
    self.book_manager.send_orders()
    book = self.session.query(Book).filter(
      Book.id == self.book_manager.book_id
    ).one()
    open_orders = book.get_open_orders()
    self.assertEqual(len(open_orders), 10)
    for order in book.get_open_orders():
      if logger.isEnabledFor(logging.DEBUG):
        self.assertIsNotNone(order.exchange_id)
    self.book_manager.close_book()

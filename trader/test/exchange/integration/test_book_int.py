import logging.config
import unittest

import config
from trader.database.db import dal
from trader.database.models.book import Book

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class TestBookIntegration(unittest.TestCase):

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

  def test_init(self):
    book = self.session.query(Book).filter(Book.id == self.book_id).one()
    self.assertIsNotNone(book)
    self.assertEqual(book.pair, "BTC-USD")
    self.assertEqual(book.get_all_orders(), [])
    self.assertEqual(book.get_ready_orders(), [])
    self.assertEqual(book.get_open_orders(), [])
    self.assertEqual(book.get_filled_orders(), [])
    self.assertEqual(book.get_canceled_orders(), [])
    self.assertEqual(book.get_ready_orders(), [])

  # def test_add_ready_order(self):
  #   book = self.session.query(Book).filter(Book.id == self.book_id).one()
  #   order = Order()



  # def test_add_order(self):
  #   book = self.session.query(Book).filter(Book.id == self.book_id).one()
  #   book.add_order("buy", "1", "1")
  #   order = self.session.query(Order).filter(
  #     Order.book_id == self.book_id).one()
  #   self.assertEqual(len(book.get_ready_orders()), 1)
  #   self.assertEqual(order.side, "buy")
  #   self.assertEqual(order.price, Decimal("1"))
  #   self.assertEqual(order.size, Decimal("1"))

  # def test_send_order(self):
  #
  #   book = self.session.query(Book).filter(Book.id == self.book_id).one()
  #   order = book.add_order("buy", "1", "1")
  #
  #   sent_order = book.send_order(order)
  #   self.assertEqual(order, sent_order)
  #   self.assertEqual(order.side, "buy")
  #   self.assertEqual(order.size, Decimal("1"))
  #   self.assertEqual(order.price, Decimal("1"))

  # @patch("trader.exchange.persisted_book.trading.get_first_book",
  #        side_effect=[
  #          # Buy part of test
  #          resources.mock_get_first_book(
  #            "102.22", "102.23"
  #          ),
  #          resources.mock_get_first_book(
  #            "101.11", "101.13"
  #          ),
  #          resources.mock_get_first_book(
  #            "99.98", "100"
  #          ),
  #          # Sell part of test
  #          resources.mock_get_first_book(
  #            "95.34", "96.23"
  #          ),
  #          resources.mock_get_first_book(
  #            "98.98", "99.99"
  #          ),
  #          resources.mock_get_first_book(
  #            "98.99", "100"
  #          )
  #        ])
  # @patch("trader.exchange.persisted_book.trading.get_product",
  #        side_effect=lambda p, test=True: resources.btc_usd_product_return)
  # @patch("trader.exchange.persisted_book.trading.confirm_order",
  #        side_effect=lambda o: mock_confirm_order(o)
  #        )
  # @patch("trader.exchange.persisted_book.trading.send_order",
  #        side_effect=lambda o: mock_send_order_rejected_above_100(o))

  def prep_db(self):
    book = Book("BTC-USD")
    self.session.add(book)
    self.session.commit()
    self.book_id = book.id

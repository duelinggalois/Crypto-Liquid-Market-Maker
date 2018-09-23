import unittest
from ..sequence.book_manager import Book_Manager
from ..sequence.trading_terms import TradingTerms
from ..exchange import trading


class TestBookManager(unittest.TestCase):

  def setUp(self):
    mid_price = trading.get_mid_market_price("ETH-USD", test=True)
    low_price = mid_price * .5
    self.terms = TradingTerms("ETH-USD", 1000, .01, .005, low_price, test=True)
    self.book_manager = Book_Manager(self.terms, test=True)

  def test_book_manager_init(self):
    self.assertEqual(self.terms, self.book_manager.terms)

    book = self.book_manager.book
    self.assertEqual(book.pair, "ETH-USD")
    self.assertEqual(len(book.unsent_orders), 39)

    buy_list = [order.price * order.size for order in book.unsent_orders
                if order.side == "buy"]
    buy_budget = round(sum(buy_list), 2)

    self.assertEqual(buy_budget, 476.41)

    sell_list = [order.size for order in book.unsent_orders
                 if order.side == "sell"]
    sell_budget = sum(sell_list) * self.terms.mid_price
    sell_budget = round(sell_budget, 2)

    self.assertEqual(sell_budget, 543.38)

  def test_book_manager_send_orders(self):

    self.book_manager.send_orders()
    book = self.book_manager.book

    self.assertEqual(book.unsent_orders, [])
    self.assertEqual(len(book.open_orders), 39)

    trading.get_open_orders(test=True)

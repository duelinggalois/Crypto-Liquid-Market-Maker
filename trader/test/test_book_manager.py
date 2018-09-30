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

    buy_list = [round(order.price * order.size, 2) for order in book.unsent_orders
                if order.side == "buy"]
    buy_budget = round(sum(buy_list), 2)

    sell_list = [order.size for order in book.unsent_orders
                 if order.side == "sell"]
    sell_budget = sum(sell_list) * self.terms.mid_price
    sell_budget = round(sell_budget, 2)
    budget = sell_budget + buy_budget
    upper_bound = self.terms.budget
    rounded_off_buy_trade = ((book.unsent_orders[25].size - self.terms.size_change) *
                             (book.unsent_orders[25].price + self.terms.price_change))
    rounded_off_sell_trade = (book.unsent_orders[51].size + self.terms.size_change) * self.terms.mid_price
    lower_bound = 1000 - rounded_off_buy_trade - rounded_off_sell_trade - 10 # TODO: understand errror trerm, guessing it has to do with price distribution.
    self.assertLessEqual(budget, upper_bound)
    self.assertGreaterEqual(budget, lower_bound)

  def test_book_manager_send_orders(self):

    starting_orders = {order["id"] for order in trading.get_open_orders("ETH-USD", test=True)}
    while len(starting_orders) != 0:
      cancel_orders = [trading.cancel_order_by_id(order, test=True) for order in starting_orders]
      starting_orders = {order["id"] for order in trading.get_open_orders("ETH-USD", test=True)}
    self.book_manager.send_orders()

    self.assertEqual(self.book_manager.book.unsent_orders, [])
    sent_order_ids = {order.id for order in self.book_manager.book.open_orders}
    ending_order_ids = {order["id"] for order in trading.get_open_orders("ETH-USD", test=True)}
    self.assertEqual(ending_order_ids, sent_order_ids)





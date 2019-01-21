import unittest
from decimal import Decimal

from ..sequence.book_manager import BookManager
from ..sequence.trading_terms import TradingTerms
from ..exchange import trading


class TestBookManager(unittest.TestCase):

  def setUp(self):
    mid_price = trading.get_mid_market_price("BTC-USD", test=True)
    low_price = mid_price / 2
    self.terms = TradingTerms("BTC-USD", "10000", ".01", ".15", low_price,
                              test=True)
    self.BookManager = BookManager(self.terms, test=True)
    starting_orders = {order["id"] for order in trading
                       .get_open_orders("BTC-USD", test=True)
                       }
    while len(starting_orders) != 0:
      [trading.cancel_order_by_id(id, test=True) for id in starting_orders]
      starting_orders = {order["id"] for order in trading
                         .get_open_orders("BTC-USD", test=True)
                         }

  def test_BookManager_init(self):
    self.assertEqual(self.terms, self.BookManager.terms)

    book = self.BookManager.book
    self.assertEqual(book.pair, "BTC-USD")

    buy_list = [round(order.price * order.size, 2)
                for order in book.unsent_orders
                if order.side == "buy"]
    buy_budget = round(sum(buy_list), 2)

    sell_list = [order.size for order in book.unsent_orders
                 if order.side == "sell"]
    sell_budget = sum(sell_list) * self.terms.mid_price
    sell_budget = round(sell_budget, 2)
    budget = sell_budget + buy_budget
    upper_bound = self.terms.budget
    last_buy = int(self.terms.count / 2 - 1)
    last_sell = int(self.terms.count - 1)
    rounded_off_buy_trade = ((book.unsent_orders[last_buy].size -
                              self.terms.size_change) *
                             (book.unsent_orders[last_buy].price +
                              self.terms.price_change))
    rounded_off_sell_trade = (book.unsent_orders[last_sell].size +
                              self.terms.size_change) * self.terms.mid_price
    lower_bound = 1000 - rounded_off_buy_trade - rounded_off_sell_trade - 10
    # TODO: understand need for error term of 10, guessing it has to do with 
    # price distribution.
    self.assertLessEqual(budget, upper_bound)
    self.assertGreaterEqual(budget, lower_bound)

  def test_BookManager_send_orders(self):
    self.BookManager.send_orders()

    self.assertEqual(self.BookManager.book.unsent_orders, [])
    sent_order_ids = {order.id for order in self.BookManager.book.open_orders}
    ending_order_ids = {order["id"] for order in trading
                        .get_open_orders("BTC-USD", test=True)}
    self.assertEqual(ending_order_ids, sent_order_ids)

    canceled_order_ids = {trading.cancel_order_by_id(id, test=True)[0]
                          for id in sent_order_ids}
    self.assertEqual(sent_order_ids, canceled_order_ids)
    no_orders_left = {order["id"] for order in trading
                      .get_open_orders("BTC-USD", test=True)}
    self.assertEqual(set(), no_orders_left)

  def test_BookManager_add_and_send_order(self):
    self.BookManager.send_orders()
    first_size = self.terms.min_size
    first_price = round(self.terms.mid_price -
                        self.terms.price_change * Decimal(".75"))
    count = int(self.terms.trade_count / 4)
    self.BookManager.add_and_send_orders("buy",
                                         count, first_size,
                                         first_price,
                                         self.terms.size_change)

    sent_order_ids = {order.id for order in self.BookManager.book.open_orders}
    ending_order_ids = {order["id"] for order in trading
                        .get_open_orders("BTC-USD", test=True)}

    self.assertEqual(sent_order_ids, ending_order_ids)

    canceled_order_ids = {trading.cancel_order_by_id(id, test=True)[0]
                          for id in sent_order_ids}
    self.assertEqual(sent_order_ids, canceled_order_ids)
    no_orders_left = {order["id"] for order in
                      trading.get_open_orders("BTC-USD", test=True)}
    self.assertEqual(set(), no_orders_left)

import unittest
import config
from ..sequence.trading_terms import TradingTerms


class test_trading_terms(unittest.TestCase):

  def setUp(self):
    self.terms = TradingTerms(test=True)

  def test_terms_init(self):

    self.assertEqual(config.CB_SUPPORTED_PAIRS, self.terms.supported_pairs)
    self.assertEqual(self.terms._base_pair, None)
    self.assertEqual(self.terms._quote_pair, None)
    self.assertEqual(self.terms._pair, None)
    self.assertEqual(self.terms._price_decimals, None)
    self.assertEqual(self.terms._budget, None)
    self.assertEqual(self.terms._min_size, None)
    self.assertEqual(self.terms._size_change, None)
    self.assertEqual(self.terms._low_price, None)
    self.assertEqual(self.terms._mid_price, None)
    self.assertEqual(self.terms._high_price, None)
    with self.assertRaises(ValueError):
      self.terms.set_mid_price()

  def test_terms_pair(self):
    self.terms = TradingTerms(test=True)
    self.terms.pair = "BTC-USD"

    self.assertEqual(self.terms.pair, "BTC-USD")
    self.assertEqual(self.terms.base_pair, "BTC")
    self.assertEqual(self.terms.quote_pair, "USD")
    self.assertEqual(self.terms.min_size, .01)
    self.assertEqual(self.terms.price_decimals, 2)

    with self.assertRaises(ValueError):
      self.terms.pair = "ETH"
    with self.assertRaises(ValueError):
      self.terms.pair = 6

    terms = TradingTerms("LTC-BTC", test=True)

    self.assertEqual(terms.pair, "LTC-BTC")
    self.assertEqual(terms.min_size, .1)
    self.assertEqual(terms.price_decimals, 5)

    with self.assertRaises(ValueError):
      terms.quote_pair = "ETH"
    with self.assertRaises(ValueError):
      terms.base_pair = "USD"

  def test_terms_budget(self):
    with self.assertRaises(ValueError):
      self.terms.budget

    self.terms.budget = 100

    self.assertEqual(self.terms.budget, 100)
    with self.assertRaises(ValueError):
      self.terms.budget = 0
    with self.assertRaises(ValueError):
      self.terms.budget = -1

  def test_min_size(self):
    with self.assertRaises(ValueError):
      self.terms.min_size
    with self.assertRaises(ValueError):
      self.terms.min_size = 1

    self.terms.pair = "ETH-USD"
    self.assertEqual(self.terms.min_size, .01)
    with self.assertRaises(ValueError):
      self.terms.min_size = .009

    self.terms.min_size = .011
    self.assertEqual(self.terms.min_size, .011)

    self.terms.pair = "LTC-USD"
    self.assertEqual(self.terms.min_size, .1)
    with self.assertRaises(ValueError):
      self.terms.min_size = .09

    self.terms.min_size = .11
    self.assertEqual(self.terms.min_size, .11)

  def test_terms_size_change(self):
    with self.assertRaises(ValueError):
      self.terms.size_change
    self.terms.size_change = .0001
    self.assertEqual(self.terms.size_change, .0001)
    with self.assertRaises(ValueError):
      self.terms.size_change = -.0001

  def test_terms_mid_price(self):
    with self.assertRaises(ValueError):
      self.terms.mid_price
    self.terms.pair = "ETH-USD"

    self.terms.set_mid_price()
    self.assertEqual(round(self.terms._mid_price, 2), self.terms.mid_price)

  def test_terms_prices(self):
    self.terms.pair = "ETH-USD"
    with self.assertRaises(ValueError):
      self.terms.high_price
    with self.assertRaises(ValueError):
      self.terms.low_price

    self.terms.set_mid_price()
    high = self.terms.mid_price + 16.67
    low = self.terms.mid_price - 16.67
    self.terms.low_price = low
    self.assertEqual(low, self.terms.low_price)
    self.assertEqual(high, self.terms.high_price)

    low_2 = round(self.terms.mid_price - 9.98, 2)
    high_2 = round(self.terms.mid_price + 9.98, 2)

    self.terms.high_price = high_2
    self.assertEqual(high, self.terms.high_price)

    self.terms._low_price = None
    self.terms.high_price = high_2
    self.assertEqual(high_2, self.terms.high_price)
    self.assertEqual(low_2, self.terms.low_price)

    self.terms.low_price = low
    self.assertEqual(low, self.terms.low_price)
    self.assertEqual(high, self.terms.high_price)

    high = self.terms.mid_price - 1
    low = self.terms.mid_price + 1
    with self.assertRaises(ValueError):
      self.terms.high_price = high
    with self.assertRaises(ValueError):
      self.terms.low_price = low

  def test_terms_str(self):
    self.terms.pair = "ETH-USD"
    self.terms.budget = 10000
    self.terms.size_change = .001
    self.terms.set_mid_price()
    self.terms.low_price = self.terms.mid_price - 100

    mid = self.terms.mid_price
    low = mid - 100
    high = mid + 100
    count = self.terms.trade_count
    price_change = self.terms.price_change

    test_output = (
      "base currency: \t\t\t{}\nquote currency: \t\t\t{}\nbudget: \t\t{}\n"
      "min size: \t\t{}\nsize change: \t\t{}\nlow price: \t\t{}\n"
      "mid price: \t\t{}\nhigh price: \t\t\t{}\ntrade_count: \t\t\t{}\n"
      "price change: \t\t{}\n"
    ).format("ETH", "USD", 10000, .01, .001, low, mid, high, count,
             price_change)

    self.assertEqual(str(self.terms), test_output)

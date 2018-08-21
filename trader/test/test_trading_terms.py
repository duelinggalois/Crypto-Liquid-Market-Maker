import unittest
import config
from ..sequence.trading_terms import TradingTerms


class test_trading_terms(unittest.TestCase):

  def test_terms_init(self):
    terms = TradingTerms(test=True)

    self.assertEqual(config.CB_SUPPORTED_PAIRS, terms.supported_pairs)

  def test_terms_pair(self):
    terms = TradingTerms(test=True)
    terms.pair = "BTC-USD"

    self.assertEqual(terms.pair, "BTC-USD")
    self.assertEqual(terms.base_pair, "BTC")
    self.assertEqual(terms.quote_pair, "USD")
    self.assertEqual(terms.min_size, .01)
    self.assertEqual(terms.price_decimals, 2)

    with self.assertRaises(ValueError):
      terms.pair = "ETH"
    with self.assertRaises(ValueError):
      terms.pair = 6

    terms = TradingTerms("LTC-BTC", test=True)

    self.assertEqual(terms.pair, "LTC-BTC")
    self.assertEqual(terms.min_size, .1)
    self.assertEqual(terms.price_decimals, 5)

    with self.assertRaises(ValueError):
      terms.quote_pair = "ETH"
    with self.assertRaises(ValueError):
      terms.base_pair = "USD"

  def test_terms_budget(self):
    terms = TradingTerms(test=True)
    terms.budget = 100

    self.assertEqual(terms.budget, 100)
    with self.assertRaises(ValueError):
      terms.budget = 0
    with self.assertRaises(ValueError):
      terms.budget = -1

  def test_terms_size_change(self):
    terms = TradingTerms(test=True)
    terms.size_change = .0001
    self.assertEqual(terms.size_change, .0001)
    with self.assertRaises(ValueError):
      terms.size_change = -.0001

  def test_terms_prices(self):
    terms = TradingTerms("BTC-USD", test=True)

    terms.low_price = 2500




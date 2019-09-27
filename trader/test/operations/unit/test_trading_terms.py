import unittest
from decimal import Decimal

import config
from trader.database.models.trading_terms import TradingTerms, ZERO, \
  TradingTermsBase


class TestTradingTerms(unittest.TestCase):

  def setUp(self):
    self.terms = TradingTerms()

  def test_terms_init(self):

    self.assertEqual(self.terms._pair, None)
    self.assertEqual(self.terms._budget, None)
    self.assertEqual(self.terms._min_size, None)
    self.assertEqual(self.terms._size_change, None)
    self.assertEqual(self.terms._low_price, None)
    self.assertEqual(self.terms._mid_price, None)
    self.assertEqual(self.terms._high_price, None)
    with self.assertRaises(ValueError):
      self.terms.set_mid_price()

  def test_terms_pair(self):
    self.terms.pair = "BTC-USD"

    self.assertEqual(self.terms.pair, "BTC-USD")
    self.assertEqual(self.terms.base_pair, "BTC")
    self.assertEqual(self.terms.quote_pair, "USD")
    self.assertEqual(type(self.terms.min_size), Decimal,
                     msg="min_size is a Decimal")
    self.assertGreater(self.terms.min_size, 0, msg="min_size is positive")
    self.assertEqual(type(self.terms.price_decimals), int,
                     msg="price_decimals is a n integer")
    self.assertGreater(self.terms.price_decimals, 0,
                       msg="price_decimal is positive")

    with self.assertRaises(ValueError):
      self.terms.pair = "ETH"
    with self.assertRaises(ValueError):
      self.terms.pair = 6

    terms = TradingTermsBase("ETH-BTC")

    self.assertEqual(terms.pair, "ETH-BTC")

  def test_terms_budget(self):
    self.assertEqual(self.terms.budget, ZERO)

    self.terms.budget = 100

    self.assertEqual(self.terms.budget, 100)
    with self.assertRaises(ValueError):
      self.terms.budget = 0
    with self.assertRaises(ValueError):
      self.terms.budget = -1

  def test_min_size(self):
    self.assertEqual(self.terms.min_size, ZERO)
    with self.assertRaises(ValueError):
      self.terms.min_size = -.001

    self.terms.pair = "ETH-BTC"
    self.assertEqual(self.terms.min_size, Decimal(".01"))
    with self.assertRaises(ValueError):
      self.terms.min_size = .009

    self.terms.min_size = ".011"
    self.assertEqual(self.terms.min_size, Decimal(".011"))
    with self.assertRaises(ValueError):
      self.terms.min_size = ".009"

  def test_terms_size_change(self):
    self.assertEqual(self.terms.size_change, ZERO)
    self.terms.size_change = .0001
    self.assertEqual(self.terms.size_change, Decimal(".0001"))
    with self.assertRaises(ValueError):
      self.terms.size_change = -.0001

  def test_terms_mid_price(self):
    self.assertEqual(self.terms.mid_price, ZERO)
    self.terms.pair = "BTC-USD"

    self.terms.set_mid_price()
    self.assertEqual(round(self.terms._mid_price, 2), self.terms.mid_price)

  def test_terms_prices(self):
    self.terms.pair = "BTC-USD"
    self.assertEqual(self.terms.high_price, ZERO)
    self.assertEqual(self.terms.low_price, ZERO)

    self.terms.set_mid_price()
    high = round(self.terms.mid_price + Decimal("16.67"), 2)
    low = round(self.terms.mid_price - Decimal("16.67"), 2)
    self.terms.low_price = low
    self.assertEqual(low, self.terms.low_price)
    self.assertEqual(high, self.terms.high_price)

    low_2 = round(self.terms.mid_price - Decimal("9.98"), 2)
    high_2 = round(self.terms.mid_price + Decimal("9.98"), 2)

    self.terms.high_price = high_2
    self.assertEqual(high, self.terms.high_price)

    self.terms._low_price = None
    self.terms.high_price = high_2
    self.assertEqual(high_2, self.terms.high_price)
    self.assertEqual(low_2, self.terms.low_price)

    self.terms.low_price = low
    self.assertEqual(low, self.terms.low_price)
    self.assertEqual(high, self.terms.high_price)

    # Set high price to 521
    highest = round(self.terms.mid_price + 21, 2)
    self.terms.high_price = highest
    self.assertEqual(highest, self.terms.high_price)

    # set high price to 499 and low to 501 to raise error
    high = self.terms.mid_price - 1
    # set high price to 501
    low = self.terms.mid_price + 1
    # set high_price to 500
    with self.assertRaises(ValueError):
      self.terms.high_price = high
    with self.assertRaises(ValueError):
      self.terms.low_price = low

  def test_terms_budgets_skew(self):
    self.terms.pair = "BTC-USD"
    self.terms._mid_price = Decimal(400)
    self.terms._high_price = Decimal(900)
    self.terms._low_price = Decimal(100)
    self.terms._size_change = 1
    self.terms._min_size = 1
    blm_A = Decimal(300 * 3 + 200 * 5 + 100 * 7)
    bmt_A = Decimal(400 * (1 + 2))
    bth_A = Decimal(400 * (4 + 6 + 8))
    self.terms.budget = (
      (1 + Decimal(config.CB_FEE)) *
      (blm_A + bmt_A + bth_A)
    )

    expected_sell_budget = 1 + 2 + 4 + 6 + 8
    expected_quote_sell_budget = 400 * expected_sell_budget
    expected_buy_budget = blm_A

    self.assertEqual(self.terms.sell_budget, expected_sell_budget)
    self.assertEqual(self.terms.quote_sell_budget, expected_quote_sell_budget)
    self.assertEqual(self.terms.buy_budget, expected_buy_budget)

  # def test_terms_str(self):
  #   self.terms.pair = "BTC-USD"
  #   self.terms.budget = 10000
  #   self.terms.size_change = .001
  #   self.terms.set_mid_price()
  #   self.terms.low_price = self.terms.mid_price / 3
  #
  #   buy_budget = round(self.terms.buy_budget, self.terms.price_decimals)
  #   sell_budget = self.terms.sell_budget
  #   quote_sell_budget = round(
  #     self.terms.quote_sell_budget, self.terms.price_decimals
  #   )
  #   base_min_size = self.terms.base_min_size
  #   mid = self.terms.mid_price
  #   low = round(mid / 3, 2)
  #   high = round(mid * Decimal(5 / 3), 2)
  #   count = self.terms.count
  #   price_change = self.terms.price_change
  #   skew = self.terms.skew
  #
  #   test_output = (
  #     "base currency: \t\t\t{0}\nquote currency: \t\t{1}\nbudget: \t\t\t{2}\n"
  #     "buy_budget: \t\t\t{3} {1}\nsell_budget: \t\t\t{4} {0} or {5} {1}\n"
  #     "min size: \t\t\t{6}\nsize change: \t\t\t{7}\nlow price: \t\t\t{8}\n"
  #     "mid price: \t\t\t{9}\nhigh price: \t\t\t{10}\ntrade_count: \t\t\t{11}\n"
  #     "skew: \t\t\t\t{12}\nprice change: \t\t\t{13}"
  #   ).format(
  #     "BTC", "USD", "10000",
  #     buy_budget,
  #     sell_budget,
  #     quote_sell_budget,
  #     base_min_size, "0.00100000", low,
  #     mid, high, count,
  #     skew, price_change)
  #
  #   self.assertEqual(str(self.terms), test_output)

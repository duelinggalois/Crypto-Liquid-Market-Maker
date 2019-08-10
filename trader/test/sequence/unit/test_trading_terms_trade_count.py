import unittest
from decimal import Decimal

from trader.sequence.trading_terms import find_count


class test_skew(unittest.TestCase):

  def setUp(self):
    self.minimum_size_A = Decimal(1)
    self.size_change_A = Decimal(1)
    self.mid_price_A = Decimal(400)
    self.low_price_A = Decimal(100)
    self.high_price_A = Decimal(900)
    self.count_A = Decimal(8)
    self.sell_skew_A = Decimal(2)
    self.blm_A = Decimal(300 * 3 + 200 * 5 + 100 * 7)
    self.bmt_A = Decimal(400 * (1 + 2))
    self.bth_A = Decimal(400 * (4 + 6 + 8))
    self.budget_A = self.blm_A + self.bmt_A + self.bth_A

    self.minimum_size_B = Decimal(".5")
    self.size_change_B = Decimal(".25")
    self.mid_price_B = Decimal(500)
    self.low_price_B = Decimal(200)
    self.high_price_B = Decimal(1100)
    self.count_B = Decimal(9)
    self.sell_skew_B = Decimal(3)
    self.blm_B = Decimal(2.25 * 200 + 1.75 * 300 + 1.25 * 400)
    self.bmt_B = Decimal(500 * (.5 + .75 + 1))
    self.bth_B = Decimal(500 * (1.5 + 2 + 2.5))
    self.budget_B = self.blm_B + self.bmt_B + self.bth_B

    self.minimum_size_C = Decimal(10)
    self.size_change_C = Decimal(20)
    self.mid_price_C = Decimal(2000)
    self.low_price_C = Decimal(1700)
    self.high_price_C = Decimal(2400)
    self.count_C = Decimal(7)
    self.sell_skew_C = Decimal(1)
    self.blm_C = Decimal(110 * 1700 + 70 * 1800 + 30 * 1900)
    self.bmt_C = Decimal(2000 * (10))
    self.bth_C = Decimal(2000 * (50 + 90 + 130))
    self.budget_C = self.blm_C + self.bmt_C + self.bth_C

    self.minimum_size_D = Decimal(1)
    self.size_change_D = Decimal(1)
    self.mid_price_D = Decimal(2000)
    self.low_price_D = Decimal(1700)
    self.high_price_D = Decimal(2300)
    self.count_D = Decimal(6)
    self.sell_skew_D = Decimal(0)
    self.blm_D = Decimal(5 * 1700 + 3 * 1800 + 1 * 1900)
    self.bmt_D = Decimal(0)
    self.bth_D = Decimal(2000 * (2 + 4 + 6))
    self.budget_D = self.blm_D + self.bmt_D + self.bth_D

  def test_find_count_A(self):
    count_A = find_count(self.minimum_size_A, self.size_change_A,
                         self.low_price_A, self.mid_price_A,
                         self.high_price_A, self.budget_A)

    self.assertEqual(self.count_A, count_A)

  def test_find_count_B(self):
    count_B = find_count(self.minimum_size_B, self.size_change_B,
                         self.low_price_B, self.mid_price_B,
                         self.high_price_B, self.budget_B)

    self.assertEqual(self.count_B, count_B)

  def test_find_count_C(self):
    count_C = find_count(self.minimum_size_C, self.size_change_C,
                         self.low_price_C, self.mid_price_C,
                         self.high_price_C, self.budget_C)

    self.assertEqual(self.count_C, count_C)

  def test_find_count_D(self):
    count_D = find_count(self.minimum_size_D, self.size_change_D,
                         self.low_price_D, self.mid_price_D,
                         self.high_price_D, self.budget_D)

    self.assertEqual(self.count_D, count_D)

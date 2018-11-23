import math
import config
from ..exchange import trading


class TradingTerms():

  def __init__(
    self,
    pair=None,
    budget=None,
    min_size=None,
    size_change=None,
    low_price=None,
    test=False):

    self._base_pair = None
    self._quote_pair = None
    self._pair = None
    self._price_decimals = None
    self._budget = None
    self._min_size = None
    self._size_change = None
    self._low_price = None
    self._mid_price = None
    self._high_price = None

    self.test = test
    self.supported_pairs = config.CB_SUPPORTED_PAIRS
    self.default_pair_index = 0
    self.pair = pair
    self.budget = budget
    self.min_size = min_size
    self.size_change = size_change
    self.low_price = low_price

  @property
  def pair(self):
    return self._pair

  @pair.setter
  def pair(self, value):
    if value and value not in self.supported_pairs:
      raise ValueError("supplied pair '{}' is not supported".format(value))

    self._pair = value
    if value:
      # split pair into pertinent parts
      self.base_pair = self.pair[:3]
      self.quote_pair = self.pair[4:]

      # Set Price rounding for USD pairs and non USD pairs
      if self.quote_pair == 'USD':
        self.price_decimals = 2
      else:
        self.price_decimals = 5

      # Assign min_price if None
      if self.base_pair == "LTC":
        self.min_size = .1
      else:
        self.min_size = .01

  # add definition of base_pair property here
  @property
  def base_pair(self):
    return self._base_pair

  @base_pair.setter
  def base_pair(self, value):
    if value not in [pair[:3] for pair in config.CB_SUPPORTED_PAIRS]:
      raise ValueError("Base currency {} not supported".format(value))
    self._base_pair = value

  # add definition of quote_pair property here
  @property
  def quote_pair(self):
    return self._quote_pair

  @quote_pair.setter
  def quote_pair(self, value):
    if value not in [pair[4:] for pair in config.CB_SUPPORTED_PAIRS]:
      raise ValueError("Quote currency {} not supported".format(value))
    self._quote_pair = value

  # add definition of price_decimals property here
  @property
  def price_decimals(self):
    return self._price_decimals

  @price_decimals.setter
  def price_decimals(self, value):
    self._price_decimals = value

  # add definition of budget property here
  @property
  def budget(self):
    if self._budget is None:
      raise ValueError("Budget has not been set yet")
    return self._budget

  @budget.setter
  def budget(self, value):
    if value or value == 0:
      if value <= 0:
        raise ValueError('Budget must be greater than 0')
      self._budget = value

  # add definition of min_size property here
  @property
  def min_size(self):
    if self._min_size is not None:
      return self._min_size
    else:
      raise ValueError("Can't get minimum size without knowing pair")

  @min_size.setter
  def min_size(self, value):
    if value:
      if self.base_pair is None:
        raise ValueError("Can't set minimum size without knowing pair")
      elif self.base_pair == "LTC" and value < .1:
        raise ValueError(
          "Minimum trade size for {} is .1".format(
            self.pair
          )
        )
      elif value < .01:
        raise ValueError(
          'Miminum size trade for {} is .01'.format(
            self.pair
          )
        )
      else:
        self._min_size = value

  # add definition of size_change property here
  @property
  def size_change(self):
    if self._size_change is None:
      raise ValueError("Size has not been set yet")
    return round(self._size_change, 8)

  @size_change.setter
  def size_change(self, value):
    if value:
      if value < 0:
        raise ValueError('Size change must be greater than or equal to 0')
      self._size_change = value

  # add definition of low_price property here
  @property
  def low_price(self):
    if self._low_price is None:
      raise ValueError("Low price has yet to be assigned.")
    else:
      return round(self._low_price, self.price_decimals)

  @low_price.setter
  def low_price(self, low_price):
    if low_price:
      if low_price < self.mid_price:
        self._low_price = low_price
        print("With mid price of {} low price was set to {}"
              .format(self.mid_price, self.low_price))
        if self._high_price is None:
          self._high_price = 2 * self.mid_price - low_price
          print("No high price so it was set to {}".format(self.high_price))
        elif self.mid_price - low_price >= self._high_price - self.mid_price:
          self._high_price = 2 * self.mid_price - low_price
          print("Raised high price to {} based on low and mid price"
                .format(self.high_price))
      else:
        raise ValueError("Low price {} is higher than mid price {}".format(
          low_price, self.mid_price)
        )

  # add definition of mid_price property here
  @property
  def mid_price(self):
    if self.pair is None:
      raise ValueError(
        "Cannot establish prices without first establishing a pair")
    elif self._mid_price is None:
      self.set_mid_price()
      return round(self._mid_price, self.price_decimals)
    else:
      return round(self._mid_price, self.price_decimals)

  def set_mid_price(self):
    if self.pair:
      self._mid_price = trading.get_mid_market_price(self.pair, test=self.test)
      print("{} currently trading at {}".format(self.pair, self.mid_price))
    else:
      raise ValueError("Pair required to get mid market price.")

  # add definition of high_price property here
  @property
  def high_price(self):
    if self._high_price is None:
      raise ValueError("High price has yet to be assigned.")
    else:
      return round(self._high_price, self.price_decimals)

  @high_price.setter
  def high_price(self, high_price):
    if high_price:
      if self.mid_price < high_price:
        if self._low_price is None:
          self._high_price = high_price
          self._low_price = 2 * self.mid_price - high_price
          print("With mid price of {} high price was set to {}"
                .format(self.mid_price, self.high_price))
          print("No low price so it was set to {}".format(self.low_price))
        elif self.mid_price - self.low_price <= high_price - self.mid_price:
          self._high_price = high_price
          print("With mid price of {} high price was set to {}")
        else:
          self._high_price = 2 * self.mid_price - self._low_price
          print("high price was raised to {} based on mid and low price."
                .format(self.high_price))
      else:
        raise ValueError(
          "High price {} must be greater than mid _price {}".format(
            high_price, self. mid_price
          )
        )

  @property
  def trade_count(self):
    print("Calculating trade count with budget of {}".format(self.budget))
    budget_considering_fee = self.budget / (1 + config.CB_FEE)
    count = find_count(self.min_size, self.size_change, self.low_price,
                      self.mid_price, self.high_price, budget_considering_fee)
    print("Count set to {}".format(count))
    return count

  @property
  def price_change(self):
    increment = (self.high_price - self.low_price) / (self.trade_count)
    return round(increment, self._price_decimals)

  def __str__(self):
    output = (
      "base currency: \t\t\t{}\nquote currency: \t\t\t{}\nbudget: \t\t{}\n"
      "min size: \t\t{}\nsize change: \t\t{}\nlow price: \t\t{}\n"
      "mid price: \t\t{}\nhigh price: \t\t\t{}\ntrade_count: \t\t\t{}\n"
      "price change: \t\t{}\n"
    ).format(
        self.base_pair, self.quote_pair, self.budget, self.min_size,
        self.size_change, self.low_price, self.mid_price, self.high_price,
        self.trade_count, self.price_change)
    return output


def find_count(S0, SD, PL, PM, PH, BU):
  A = (SD * (3 * PH ** 2 * PM - 3 * PH * PL ** 2 - 3 * PH * PM ** 2 +
             PL ** 3 + 3 * PL ** 2 * PM - 3 * PL * PM ** 2 + 2 * PM ** 3))

  B = (3 * (PH - PL) * (PH * PL * SD + 2 * PH * PM * S0 - 2 * PH * PM * SD +
                        -PL ** 2 * S0 + PL ** 2 * SD - 2 * PL * PM * SD +
                        -PM ** 2 * S0 + 2 * PM ** 2 * SD))

  C = (-6 * BU * (PH - PL) ** 2 +
       (PH - PL) ** 2 * (PL - PM) * (3 * S0 - 4 * SD))

  return int((-B + math.sqrt(B ** 2 - 4 * A * C)) / (2 * A))

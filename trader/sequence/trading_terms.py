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

    self.supported_pairs = config.CB_SUPPORTED_PAIRS
    self.default_pair_index = 0
    self.pair = pair
    self.test = test

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
    return self._budget

  @budget.setter
  def budget(self, value):
    if value <= 0:
      raise ValueError('Budget must be greater than 0')
    self._budget = value

  # add definition of min_size property here
  @property
  def min_size(self):
    return self._min_size

  @min_size.setter
  def min_size(self, value):
    if self.base_pair == "LTC" and value < .1:
      raise ValueError(
        "Minimum trade size for {} is .1".fromat(
          self.pair
        )
      )
    elif value < .01:
      ValueError(
        'Miminum size trade for {} is .01'.format(
          self.pair
        )
      )
    self._min_size = value

  # add definition of size_change property here
  @property
  def size_change(self):
    return self._size_change

  # not sure if size_change can be 0
  @size_change.setter
  def size_change(self, value):
    if value < 0:
      raise ValueError('Size change must be greater than or equal to 0')
    self._size_change = value

  # add definition of low_price property here
  @property
  def low_price(self):
    if self._low_price is None:
      raise ValueError("Low price has yet to be assigned.")
    else:
      return self._low_price

  @low_price.setter
  def low_price(self, low_price):
    if low_price < self.mid_price:
      self._low_price = low_price
      self._high_price = 2 * self.mid_price - low_price
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
    else:
      self._mid_price = trading.get_mid_market_price(self.pair, test=self.test)
    return self._mid_price

  # add definition of high_price property here
  @property
  def high_price(self):
    if self._high_price is None:
      raise ValueError("High price has yet to be assigned.")
    else:
      return self._high_price

  @high_price.setter
  def high_price(self, high_price):
    if self.mid_price < high_price:
      self._high_price = high_price
      self._low_price = 2 * self.mid_price - high_price
    else:
      raise ValueError(
        "High price {} must be greater than mid _price {}".format(
          high_price, self. mid_price
        )
      )

  # add definition of max_trades property here
  @property
  def max_trades(self):
    '''
    Using a budget in terms of the denominator of a trading pair (USD for
    BTC-USD), min_size and size_change of trade amounts, and a price range
    for trade values in terms of low_price and high_price this function will
    give you the maximoum possible trades that can be used in a sequence of
    alternating increasing buy and sell trades.

    >>> get_max_trades(193, .01, .005, 500, 1300)
    8
    '''

    # ensure required properties are set
    if (self._size_change is None):
      raise ValueError('size change not set')
    if (self._high_price is None):
      raise ValueError('high price not set')
    if (self._min_size is None):
      raise ValueError('min price not set')
    if (self._budget is None):
      raise ValueError('budget not set')

    # capturing into var to prevent duplicate recomputation, there's likely a
    # better way to do this
    low_price = self.low_price

    # determine coefficients
    A = 12 * self.size_change * self.mid_price
    B = 3 * (self.mid_price *
             (4 * self.min_size - 3 * self.size_change) +
             self.size_change * low_price)
    C = -3 * (self.size_change *
              (self.high_price - self.mid_price) +
              2 * self.budget)

    # grind it through quadratic formula
    trades = (-B + math.sqrt(B ** 2 - 4 * A * C)) / (2 * A)

    # double the result to account for both buys/sells
    return 2 * int(trades)

  # add definition of price_change property here
  @property
  def price_change(self):
    increment = (self.high_price - self.mid_price) / (self.max_trades / 2)
    return round(increment, self._price_decimals)

  def __str__(self):
    output = "from: \t\t\t{}\n".format(self.base_pair)
    output += "to: \t\t\t{}\n".format(self.quote_pair)
    output += "budget: \t\t{}\n".format(self.budget)
    output += "min size: \t\t{}\n".format(self.min_size)
    output += "size change: \t\t{}\n".format(self.size_change)
    output += "low price: \t\t{}\n".format(self.low_price)
    output += "mid price: \t\t{}\n".format(self.mid_price)
    output += "high price: \t\t{}\n".format(self.high_price)
    output += "max trades: \t\t{}\n".format(self.max_trades)
    output += "price change: \t\t{}\n".format(self.price_change)
    return output

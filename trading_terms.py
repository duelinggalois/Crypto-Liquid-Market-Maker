import math

class TradingTerms():

  def __init__(
    self, 
    pair=None, 
    budget=None, 
    min_size=None,
    size_change=None,
    low_price=None,
    mid_price=None):

    self.supported_pairs = ["BTC-USD", "ETH-USD", "LTC-USD", "BCH-USD", "ETH-BTC", "LTC-BTC", "BCH-BTC"]
    self.default_pair_index = 0
    self.pair = pair
    self.budget = budget
    self.min_size = min_size
    self.size_change = size_change
    self.low_price = low_price
    self.mid_price = mid_price

  # add definition of pair property here
  @property
  def pair(self):
    return self._pair

  @pair.setter
  def pair(self, value):
    if value not in self.supported_pairs:
      raise ValueError("supplied pair '{}' is not supported".format(value))
    self._pair = value
    
    # split pair into pertinent parts
    self._pair_from = self._pair[:3]
    self._pair_to = self._pair[4:]

    # Set Price rounding for USD pairs and non USD pairs
    if self._pair_to == 'USD':
      self._p_round = 2
    else:
      self._p_round = 5

    # Assign min_price if None
    if not min_size:
      if self._pair_from == "LTC":
        self.min_size = .1
      else :
        self.min_size = .01

  # add definition of pair_from property here
  @property
  def pair_from(self):
    return self._pair_from

  # add definition of pair_to property here
  @property
  def pair_to(self):
    return self._pair_to

  # add definition of p_round property here
  @property
  def p_round(self):
    return self._p_round

  # add definition of budget property here
  @property
  def budget(self):
    return self._budget

  @budget.setter
  def budget(self, value):
    if value <= 0: ValueError('Budget must be greater than 0')
    self._budget = value

  # add definition of min_size property here
  @property
  def min_size(self):
    return self._min_size

  @min_size.setter
  def min_size(self, value):
    if self.pair_from == "LTC" and value < .1:
      ValueError("Minimum trade size for {} is .1".fromat(
        self.pair
        )
      )
    elif value < .01: ValueError('Miminum size trade for {} is .01'.format(
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
    if value <= 0: ValueError('Size change must be greater than 0')
    self._size_change = value
    
  # add definition of low_price property here
  @property
  def low_price(self):
    return _low_price

  @low_price.setter
  def low_price(self, value):
    self._low_price = low_price

  # add definition of mid_price property here
  @property
  def mid_price(self):
    return self._mid_price

  @mid_price.setter
  def mid_price(self, value):
    self._mid_price = round(value, self.p_round)

  # add definition of high_price property here
  @property
  def high_price(self):
    if (self.mid_price is None):
      raise ValueError('cannot compute high price, mid price not set')
    if (self.low_price is None):
      raise ValueError('cannot compute high price, low price not set')
    return round(
      (2 * self.mid_price) - self.low_price,
      self.p_round
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
    if (self._size_change is None): raise ValueError('size change not set')
    if (self._high_price is None): raise ValueError('high price not set')
    if (self._min_size is None): raise ValueError('min price not set')
    if (self._budget is None): raise ValueError('budget not set')
    
    # capturing into var to prevent duplicate recomputation, there's likely a better way to do this
    low_price = self.low_price

    # determine coefficients
    A = 12 * self.size_change * self.mid_price
    B = 3 * ( self.mid_price * ( 4 * self.min_size - 3 * self.size_change) + self.size_change * low_price )
    C = -3 * ( self.size_change * ( self.high_price - self.mid_price ) + 2 * self.budget ) 
    
    # grind it through quadratic formula
    trades = ( - B + math.sqrt( B ** 2 - 4 * A * C))  / (2*A)

    # double the result to account for both buys/sells
    return 2 * int(trades)

  # add definition of price_change property here
  @property
  def price_change(self):
    increment = (self.high_price - self.mid_price) / (self.max_trades / 2)
    return round(increment, self._p_round)

  def __str__(self):
    output = "from: \t\t\t{}\n".format(self.pair_from)
    output += "to: \t\t\t{}\n".format(self.pair_to)
    output += "budget: \t\t{}\n".format(self.budget)
    output += "min size: \t\t{}\n".format(self.min_size)
    output += "size change: \t\t{}\n".format(self.size_change)
    output += "low price: \t\t{}\n".format(self.low_price)
    output += "mid price: \t\t{}\n".format(self.mid_price)
    output += "high price: \t\t{}\n".format(self.high_price)
    output += "max trades: \t\t{}\n".format(self.max_trades)
    output += "price change: \t\t{}\n".format(self.price_change)
    return output

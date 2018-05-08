import math

class TradingTerms():

  supported_pairs = ["BTC-USD", "ETH-USD", "LTC-USD", "BCH-USD", "BTC-ETH", "LTC-BTC", "BCH-BTC"]
  default_pair_index = 6
  
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

    if self._pair_to == 'USD':
      self._p_round = 2
    else:
      self._p_round = 5

  # add definition of pair_from property here
  @property
  def pair_from(self):
    return self._pair_from

  # add definition of pair_to property here
  @property
  def pair_to(self):
    return self._pair_to

  # add definition of budget property here
  @property
  def budget(self):
    return self._budget

  @budget.setter
  def budget(self, value):
    self._budget = value

  # add definition of min_size property here
  @property
  def min_size(self):
    return self._min_size

  @min_size.setter
  def min_size(self, value):
    self._min_size = value

  # add definition of size_change property here
  @property
  def size_change(self):
    return self._size_change

  @size_change.setter
  def size_change(self, value):
    self._size_change = value
    
  # add definition of low_price property here
  @property
  def low_price(self):
    if (self._mid_price is None):
      raise ValueError('cannot compute low price, mid price not set')
    if (self._high_price is None):
      raise ValueError('cannot compute low price, high price not set')
    return (2 * self._mid_price) - self._high_price

  # add definition of mid_price property here
  @property
  def mid_price(self):
    return self._mid_price

  @mid_price.setter
  def mid_price(self, value):
    self._mid_price = round(value, self._p_round)

  # add definition of high_price property here
  @property
  def high_price(self):
    return self._high_price

  @high_price.setter
  def high_price(self, value):
    self._high_price = round(value, self._p_round)

  # add definition of max_trades property here
  @property
  def max_trades(self):
    '''Using a budget in terms of the denominator of a trading pair (USD for
    BTC-USD), min_size and size_change of trade amounts, and a price range
    for trade values in terms of low_price and high_price this function will 
    give you the maximoum possible trades that can be used in a sequence of 
    alternating increasing buy and sell trades. 
    
    >>> get_max_trades(193, .01, .005, 500, 1300)
    8
    '''

    # ensure required properties are set
    if (self.size_change is None): raise ValueError('size change not set')
    if (self.high_price is None): raise ValueError('high price not set')
    if (self.min_size is None): raise ValueError('min price not set')
    if (self.budget is None): raise ValueError('budget not set')
    
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

  def __init__(self):
    return
  
  def toString(self):
    print(
      " from: \t\t\t{}\n".format(self.pair_from),
      "to: \t\t\t{}\n".format(self.pair_to),
      "budget: \t\t{}\n".format(self.budget),
      "min size: \t\t{}\n".format(self.min_size),
      "size change: \t\t{}\n".format(self.size_change),
      "low price: \t\t{}\n".format(self.low_price),
      "mid price: \t\t{}\n".format(self.mid_price),
      "high price: \t\t{}\n".format(self.high_price),
      "max trades: \t\t{}\n".format(self.max_trades),
      "price change: \t\t{}\n".format(self.price_change)
    )

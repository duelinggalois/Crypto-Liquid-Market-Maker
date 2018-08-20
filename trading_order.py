class TradingOrder():


  def __init__(self, pair, side, size, price, num_trades):
    self.pair = pair
    self.side = side
    self.size = size
    self.price = price
    self.num_trades = num_trades



  # add definition of side property here
  @property
  def side(self):
    return self._side

  @side.setter
  def side(self, value):
    if value not in ["buy", "sell"]:
      raise ValueError("invalid side: must be 'buy' or 'sell'")

    self._side = value

  # add definition of size property here
  @property
  def size(self):
    return self._size

  @size.setter
  def size(self, value):
    self._size = value

  # add definition of price property here
  @property
  def price(self):
    return self._price

  @price.setter
  def price(self, value):
    self._price = value

  # add definition of num_trades property here
  @property
  def num_trades(self):
    return self._num_trades

  @num_trades.setter
  def num_trades(self, value):
    self._num_trades = value

  # add definition of pos_neg property here
  @property
  def pos_neg(self):
    return -1 if self._side == 'buy' else 1

  def __str__(self):
    return "\{side: {}, size: {}, price: {}, num_trades: {}\}".format(self.side, self.size, self.price, self.num_trades)

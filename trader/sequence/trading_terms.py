import logging
import logging.config
from pprint import pformat
from decimal import Decimal

import config
from trader.exchange.api_wrapper.noop_trader import NoopApi

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)

ZERO = Decimal("0")
ZERO_INTEGER = 0
NO_VALUE = "None"


class TradingTerms:

  def __init__(
    self,
    pair=None,
    budget=None,
    min_size=None,
    size_change=None,
    low_price=None,
    high_price=None,
    trading_api=NoopApi()
  ):

    self._base_pair = None
    self._quote_pair = None
    self._pair = None
    self._price_decimals = None
    self._budget = None
    self._base_min_size = None
    self._min_size = None
    self._size_change = None
    self._low_price = None
    self._mid_price = None
    self._high_price = None
    self._price_change = None
    self._initial_count = None
    self._count = None
    self._sell_count = None
    self._buy_count = None
    self._skew = None
    self._buy_budget = None
    self._sell_budget = None
    self._quote_sell_budget = None

    self.trading_api = trading_api
    self.supported_pairs = trading_api.get_products()
    self.pair = pair
    self.budget = budget
    self.min_size = min_size
    self.size_change = size_change
    self.low_price = low_price
    self.high_price = high_price

  @property
  def trading_api(self):
   return self._trading_api

  @trading_api.setter
  def trading_api(self, value):
    self._trading_api = value
    self.supported_pairs = self._trading_api.get_products()

  @property
  def pair(self):
    if self._pair is None:
      return NO_VALUE
    return self._pair

  @pair.setter
  def pair(self, value):
    if value is not None and value not in self.supported_pairs:
      raise ValueError("supplied pair '{}' is not supported".format(value))

    self._pair = value
    if value is not None:
      details = self.trading_api.get_product_details(value)
      # split pair into pertinent parts
      self.base_pair = details["base_currency"]
      self.quote_pair = details["quote_currency"]
      # price_decimal is used to round, we want to exclude "0." from length
      self.price_decimals = len(details["quote_increment"].rstrip("0")) - 2
      self.base_min_size = details["base_min_size"].rstrip("0")
      self.quote_increment = details["quote_increment"].rstrip("0")
      self.min_size = details["base_min_size"].rstrip("0")
      self.max_size = details["base_max_size"].rstrip("0")

  # add definition of base_pair property here
  @property
  def base_pair(self):
    if self._base_pair is None:
      return NO_VALUE
    return self._base_pair

  @base_pair.setter
  def base_pair(self, value):
    if value not in [pair.split("-")[0] for pair in self.supported_pairs]:
      raise ValueError("Base currency {} not supported".format(value))
    self._base_pair = value

  @property
  def base_min_size(self):
      if self._base_min_size is None:
        return ZERO
      return self._base_min_size

  @base_min_size.setter
  def base_min_size(self, value):
    self._base_min_size = value

  @property
  def quote_pair(self):
    if self._quote_pair is None:
      return NO_VALUE
    return self._quote_pair

  @quote_pair.setter
  def quote_pair(self, value):
    if value not in [pair.split("-")[1] for pair in self.supported_pairs]:
      raise ValueError("Quote currency {} not supported".format(value))
    self._quote_pair = value

  # add definition of price_decimals property here
  @property
  def price_decimals(self):
    return self._price_decimals

  @price_decimals.setter
  def price_decimals(self, value):
    self._price_decimals = int(value)

  @property
  def budget(self):
    if self._budget is None:
      return ZERO
    return self._budget

  @budget.setter
  def budget(self, value):
    if value or value == 0:
      if Decimal(value) <= 0:
        raise ValueError('Budget must be greater than 0')
      self._budget = Decimal(value)

  @property
  def min_size(self):
    if self._min_size is None:
      return ZERO
    return self._min_size

  @min_size.setter
  def min_size(self, value):
    if value:
      if Decimal(value) < Decimal(self.base_min_size):
        raise ValueError(
          "Minimum trade size for {} is {}".format(
            self.pair, self.base_min_size
          )
        )
      else:
        self._min_size = Decimal(value)

  # add definition of size_change property here
  @property
  def size_change(self):
    if self._size_change is None:
      return ZERO
    return round(self._size_change, 8)

  @size_change.setter
  def size_change(self, value):
    if value:
      if Decimal(value) < 0:
        raise ValueError('Size change must be greater than or equal to 0')
      self._size_change = Decimal(value)

  @property
  def low_price(self):
    if self._low_price is None:
      return ZERO
    else:
      return round(self._low_price, self.price_decimals)

  @low_price.setter
  def low_price(self, low_price):
    if low_price is not None:
      if Decimal(low_price) < self.mid_price:
        self._low_price = Decimal(low_price)
        logger.info("With mid price of {} low price was set to {}"
                    .format(self.mid_price, self.low_price))
        if self._high_price is None:
          self._high_price = 2 * self.mid_price - Decimal(low_price)
          logger.info("No high price so it was set to {}"
                      .format(self.high_price))
        elif self.mid_price - low_price >= self._high_price - self.mid_price:
          self._high_price = 2 * self.mid_price - Decimal(low_price)
          logger.warning("Raised high price to {} based on low and mid price"
                      .format(self.high_price))
      else:
        raise ValueError("Low price {} is higher than mid price {}".format(
          low_price, self.mid_price)
        )

  # add definition of mid_price property here
  @property
  def mid_price(self):
    if self.pair is NO_VALUE:
      return ZERO
    if self._mid_price is None:
      self.set_mid_price()
    return round(self._mid_price, self.price_decimals)

  def set_mid_price(self):
    if self.pair is not NO_VALUE:
      self._mid_price = self.trading_mid_market_price(self.pair)
      logger.info("{} currently trading at {}"
                  .format(self.pair, self._mid_price))
    else:
      raise ValueError("Pair required to get mid market price.")

  # add definition of high_price property here
  @property
  def high_price(self):
    if self._high_price is None:
      return ZERO
    else:
      return round(self._high_price, self.price_decimals)

  @high_price.setter
  def high_price(self, value):
    if value is not None:
      #Todo change midprice to return a decimal
      if Decimal(self.mid_price) < value:
        if self._low_price is None:
          self._high_price = Decimal(value)
          self._low_price = 2 * self.mid_price - self._high_price
          logger.info("With mid price of {} high price was set to {}"
                      .format(self.mid_price, self.high_price))
          logger.info("No low price so it was set to {}"
                      .format(self.low_price))
        elif (self.mid_price - self.low_price <=
              Decimal(value) - self.mid_price):
          self._high_price = Decimal(value)
          logger.info("With mid price of {} high price was set to {}")
        else:
          self._high_price = Decimal(2 * self.mid_price - self._low_price)
          logger.warning("high price was raised to {} based on mid and low "
                         "price."
                         .format(self.high_price))
      else:
        raise ValueError(
          "High price {} must be greater than mid _price {}".format(
            value, self. mid_price
          )
        )

  @property
  def trade_count(self):
    budget_considering_fee = self.budget / (1 + Decimal(config.CB_FEE))
    try:
      return find_count(
        self.min_size, self.size_change, self.low_price, self.mid_price,
        self.high_price, budget_considering_fee)
    except ZeroDivisionError:
      return ZERO

  @property
  def price_change(self):

    try:
      return round(Decimal(
        self.high_price - self.low_price
      ) / self.trade_count, self._price_decimals)
    except:
      return ZERO

    return self._price_change

  @property
  def count(self):
    return self.buy_count + self.sell_count

  @property
  def buy_count(self):
    if self.trade_count == 0 or self.high_price == self.low_price:
      return ZERO_INTEGER
    return int(
        (self.mid_price - self.low_price) /
        (self.high_price - self.low_price) * self.trade_count
      )

  @property
  def sell_count(self):
    if self.trade_count == 0 or self.high_price == self.low_price:
      return ZERO_INTEGER
    return int(
          (self.high_price - self.mid_price) /
          (self.high_price - self.low_price) * self.trade_count
        )

  @property
  def skew(self):
    return self.sell_count - self.buy_count

  @property
  def buy_budget(self):

    buy_price = self.mid_price - self.price_change
    buy_size = self.min_size + self.size_change * self.skew
    buy_budget = ZERO
    for i in range(self.buy_count):
      buy_budget += buy_price * buy_size
      buy_price -= self.price_change
      buy_size += 2 * self.size_change

    return buy_budget

  @property
  def sell_budget(self):
    total_size = 0
    if self.skew > 0:
      sell_size = self.min_size
      for i in range(self.skew):
        total_size += sell_size
        sell_size += self.size_change
      sell_size += self.size_change
    else:
      sell_size = self.min_size + self.size_change
    for i in range(self.sell_count - self.skew):
      total_size += sell_size
      sell_size += 2 * self.size_change
    return total_size


  @property
  def quote_sell_budget(self):
    return self.sell_budget * self.mid_price

  def __str__(self):
    parameters = [
      f for f in dir(self) if f[0] != "_" and f not in
      ("set_mid_price", "trading_mid_market_price", "supported_pairs")
    ]
    output = {
      f: str(getattr(self, f)) for f in parameters
    }
    return pformat(output, indent=4, width=4, compact=True)

  def trading_mid_market_price(self, pair):
    return Decimal(self.trading_api.get_mid_market_price(pair))


def find_count(S0, SD, PL, PM, PH, BU):
  A = (SD * (3 * PH ** 2 * PM - 3 * PH * PL ** 2 - 3 * PH * PM ** 2 +
             PL ** 3 + 3 * PL ** 2 * PM - 3 * PL * PM ** 2 + 2 * PM ** 3))
  if A == 0:
    return ZERO
  B = (3 * (PH - PL) * (PH * PL * SD + 2 * PH * PM * S0 - 2 * PH * PM * SD +
                        -PL ** 2 * S0 + PL ** 2 * SD - 2 * PL * PM * SD +
                        -PM ** 2 * S0 + 2 * PM ** 2 * SD))

  C = (-6 * BU * (PH - PL) ** 2 +
       (PH - PL) ** 2 * (PL - PM) * (3 * S0 - 4 * SD))

  return int((-B + (B ** 2 - 4 * A * C).sqrt()) / (2 * A))

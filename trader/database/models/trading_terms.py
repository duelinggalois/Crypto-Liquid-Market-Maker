import logging.config
from pprint import pformat
from decimal import Decimal, InvalidOperation

from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, Enum, \
  Boolean

import config
from trader.database.models.base_wrapper import BaseWrapper
from trader.exchange.api_enum import ApiEnum
from trader.exchange.api_provider import ApiProvider

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)

ZERO = Decimal("0")
ZERO_INTEGER = 0
NO_VALUE = "None"


class TradingTermsBase:
  def __init__(
    self,
    pair=None,
    budget=None,
    min_size=None,
    size_change=None,
    low_price=None,
    high_price=None,
    api_enum=ApiEnum.NoopApi
  ):

    self._pair = None
    self._budget = None
    self._min_size = None
    self._size_change = None
    self._low_price = None
    self._mid_price = None
    self._high_price = None
    self._supported_pairs = None

    self.api_enum = api_enum
    self.pair = pair
    self.budget = budget
    self.min_size = min_size
    self.size_change = size_change
    self.low_price = low_price
    self.high_price = high_price

  @property
  def pair(self):
    if self._pair is None:
      return NO_VALUE
    return self._pair

  @pair.setter
  def pair(self, value):
    if value is not None and value not in self.supported_pairs:
      raise ValueError("supplied pair {} is not supported".format(value))

    self._pair = value
    self.set_exchange_metadata_for_pair()

  @property
  def api_enum(self):
    if self._api_enum is None:
      return ApiEnum.NoopApi
    else:
      return self._api_enum

  @api_enum.setter
  def api_enum(self, value):
    if value not in ApiProvider.get_api_keys():
      raise ValueError(
        "Supplied value {} is not in supported list: {}".format(
          value, ApiProvider.get_api_keys()
        )
      )
    else:
      self._api_enum = value

  @property
  def trading_api(self):
    # api_enum will never be None
    return ApiProvider.get_api(self.api_enum)

  @property
  def supported_pairs(self):
    if self._supported_pairs is None:
      self._supported_pairs = self.trading_api.get_products()
    return self._supported_pairs

  @property
  def base_pair(self):
    if self._pair is None:
      return NO_VALUE
    return self._pair.split("-")[0]

  @property
  def quote_pair(self):
    if self._pair is None:
      return NO_VALUE
    return self._pair.split("-")[1]

  @property
  def budget(self):
    if self._budget is None:
      return ZERO
    return self._budget

  @budget.setter
  def budget(self, value):
    if value is not None:
      try:
        if Decimal(value) <= 0:
          raise ValueError('Budget must be greater than 0')
        self._budget = Decimal(value)
      except InvalidOperation as e:
        raise ValueError("Budget must be a number")

  @property
  def min_size(self):
    if self._min_size is None:
      return Decimal(self.base_min_size)
    return self._min_size

  @min_size.setter
  def min_size(self, value):
    if value is not None:
      try:
        if Decimal(value) < Decimal(self.base_min_size):
          raise ValueError(
            "Minimum trade size for {} is {}".format(
              self.pair, self.base_min_size
            )
          )
        else:
          self._min_size = Decimal(value)
      except InvalidOperation as e:
        raise ValueError("Minimum size must be a number")

  @property
  def size_change(self):
    if self._size_change is None:
      return ZERO
    return round(self._size_change, 8)

  @size_change.setter
  def size_change(self, value):
    if value:
      try:
        if Decimal(value) < 0:
          raise ValueError('Size change must be greater than or equal to 0')
        self._size_change = Decimal(value)
      except InvalidOperation as e:
        raise ValueError("Size change must be a number")

  @property
  def low_price(self):
    if self._low_price is None:
      return ZERO
    else:
      return round(self._low_price, self.price_decimals)

  @low_price.setter
  def low_price(self, low_price):
    if low_price is not None:
      try:
        low_price = Decimal(low_price)
        if low_price < self.mid_price:
          self._low_price = low_price
          logger.debug("With mid price of {} low price was set to {}"
                       .format(self.mid_price, self.low_price))
          if self._high_price is None:
            self._high_price = 2 * self.mid_price - low_price
            logger.debug("No high price so it was set to {}"
                         .format(self.high_price))
          elif self.mid_price - low_price >= self._high_price - self.mid_price:
            self._high_price = 2 * self.mid_price - low_price
            logger.debug("Raised high price to {} based on low and mid price"
                         .format(self.high_price))
        else:
          raise ValueError("Low price {} is higher than mid price {}".format(
            low_price, self.mid_price)
          )
      except InvalidOperation as e:
        raise ValueError("Low Price must be a number")

  @property
  def mid_price(self):
    if self.pair is NO_VALUE:
      return ZERO
    if self._mid_price is None:
      self.set_mid_price()
    return round(self._mid_price, self.price_decimals)

  def set_mid_price(self):
    if self.pair is not NO_VALUE:
      self._mid_price = self.trading_mid_market_price()
      logger.debug("{} currently trading at {}"
                   .format(self.pair, self._mid_price))
    else:
      raise ValueError("Pair required to get mid market price.")

  @property
  def high_price(self):
    if self._high_price is None:
      return ZERO
    else:
      return round(self._high_price, self.price_decimals)

  @high_price.setter
  def high_price(self, value):
    if value is not None:
      try:
        if self.mid_price < Decimal(value):
          if self._low_price is None:
            self._high_price = Decimal(value)
            self._low_price = 2 * self.mid_price - self._high_price
            logger.debug("With mid price of {} high price was set to {}"
                         .format(self.mid_price, self.high_price))
            logger.debug("No low price so it was set to {}"
                         .format(self.low_price))
          elif (self.mid_price - self.low_price <=
                Decimal(value) - self.mid_price):
            self._high_price = Decimal(value)
            logger.debug("With mid price of {} high price was set to {}"
                         .format(self.mid_price, self.high_price))
          else:
            self._high_price = Decimal(2 * self.mid_price - self._low_price)
            logger.debug("high price was raised to {} based on mid and low "
                         "price.".format(self.high_price))
        else:
          raise ValueError(
            "High price {} must be greater than mid _price {}".format(
              value, self. mid_price
            )
          )
      except InvalidOperation as e:
        raise ValueError("High price must be a number")

  @property
  def base_min_size(self):
      if self._pair is None:
        return ZERO
      if self._base_min_size is None:
        self.set_exchange_metadata_for_pair()
      return self._base_min_size

  @property
  def price_decimals(self):
    if self._pair is None:
      return ZERO_INTEGER
    if self._price_decimals is None:
      self.set_exchange_metadata_for_pair()
    return self._price_decimals

  def set_exchange_metadata_for_pair(self):
    if self._pair is not None:
      details = self.trading_api.get_product_details(self._pair)
      self._base_min_size = details["base_min_size"].rstrip("0")
      self._price_decimals = len(details["quote_increment"].rstrip("0")) - 2


  @property
  def trade_count(self):
    budget_considering_fee = self.budget / (1 + Decimal(config.CB_FEE))
    try:
      return self.find_count(
        self._min_size, self._size_change, self._low_price, self._mid_price,
        self._high_price, budget_considering_fee)
    except (ZeroDivisionError, TypeError):
      return ZERO

  @property
  def price_change(self):
    if self.trade_count != 0:
      return round((self.high_price - self.low_price) / self.trade_count,
                   self.price_decimals)
    else:
      return ZERO

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
      ("set_mid_price", "trading_mid_market_price", "supported_pairs",
       "find_count", "query", "query_class", "set_exchange_metadata_for_pair"

       )
    ]
    output = {
      f: str(getattr(self, f)) for f in parameters
    }
    return pformat(output, indent=4, width=4, compact=True)

  def trading_mid_market_price(self):
    return Decimal(self.trading_api.get_mid_market_price(self.pair))

  @staticmethod
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


class TradingTerms(TradingTermsBase, BaseWrapper):
  """Persisted Trading Terms
  """

  user_id = Column(Integer, ForeignKey('users.id'))
  active = Column(Boolean(), default=False)
  _pair = Column("pair", String(15))
  _budget = Column("budget", Numeric(precision=12, scale=4))
  _min_size = Column("min_size", Numeric(precision=7, scale=4))
  _low_price = Column("low_price", Numeric(precision=17, scale=9))
  _mid_price = Column("initial_mid_price", Numeric(precision=17, scale=9))
  _high_price = Column("high_price", Numeric(precision=17, scale=9))
  _size_change = Column("size_change", Numeric(precision=12, scale=9))
  _api_enum = Column("api_enum", Enum(ApiEnum))

  # values needed to ensure loaded object methods have needed values.
  _price_decimals = None
  _base_min_size = None
  _supported_pairs = None

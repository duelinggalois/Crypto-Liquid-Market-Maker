import time
import logging
import logging.config
from decimal import Decimal

from sqlalchemy import Column, String, Numeric, Boolean

from ..database.manager import (
  BaseWrapper, Engine, Test_Engine, test_session, session
)
import config


logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class Order(BaseWrapper):

  # Setting up database table
  _exchange_id = Column("exchange_id", String(40))
  _pair = Column("pair", String(15))
  _side = Column("side", String(4))
  _price = Column("price", Numeric(precision=13, scale=5))
  _size = Column("size", Numeric(precision=12, scale=8))
  _filled = Column("filled", Numeric(precision=12, scale=8))
  _status = Column("status", String(15))
  _post_only = Column("post_only", Boolean)
  _test = Column("test", Boolean)

  def __init__(
    self, pair, side, size, price, post_only=True, persist=True, test=False
  ):

    if test:
      self.session = test_session
      self.engine = Test_Engine
    else:
      self.session = session
      self.engine = Engine

    print("Order t" + str(self.session))

    self.pair = pair
    self.side = side
    self.size = size
    self.filled = "0"
    self.price = price
    self.status = "ready"
    self.history = []
    self.responses = []
    self.test = test
    self.post_only = post_only
    self.persist = persist

  @property
  def exchange_id(self):
    return self._exchange_id

  @exchange_id.setter
  def exchange_id(self, value):
    self._exchange_id = value

  @property
  def pair(self):
    return self._pair

  @pair.setter
  def pair(self, value):

    self._pair = value
    self.base_pair = self.pair[:3]
    self.quote_pair = self.pair[4:]

    # Set Price rounding for USD pairs and non USD pairs
    if self.quote_pair == 'USD':
      self.price_decimals = 2
    else:
      self.price_decimals = 5

  @property
  def side(self):
    return self._side

  @side.setter
  def side(self, value):
    if value not in ["buy", "sell"]:
      raise ValueError("side must be 'buy' or 'sell'.")

    self._side = value

  @property
  def price(self):
    return self._price

  @price.setter
  def price(self, value):
    self._price = round(Decimal(value), self.price_decimals)

  @property
  def size(self):
    return self._size

  @size.setter
  def size(self, value):
    self._size = Decimal(value)

  @property
  def filled(self):
    return self._filled

  @filled.setter
  def filled(self, value):
      self._filled = Decimal(value)

  @property
  def status(self):
    return self._status

  @status.setter
  def status(self, value):
    self._status = value

  @property
  def post_only(self):
    return self._post_only

  @post_only.setter
  def post_only(self, value):
    self._post_only = value

  @property
  def test(self):
    return self._test

  @test.setter
  def test(self, value):
    self._test = value

  def update_history(self, message):
    self.history.append(
      {"time": time.time(), "status": message}
    )

  def allow_market_trade(self):
    self.post_only = False

  def __str__(self):
    return (
      "pair: {}\n"
      "side: {}\n"
      "price: {}\n"
      "size: {}\n"
      "filled: {}\n"
      "status: {}\n"
      "exchange_id: {}\n"
      "test: {}\n"
      "history: {}\n"
      "responses: {}"
    ).format(
      self.pair,
      self.side,
      self.price,
      self.size,
      self.filled,
      self.status,
      self.exchange_id,
      self.test,
      self.history,
      self.responses
    )

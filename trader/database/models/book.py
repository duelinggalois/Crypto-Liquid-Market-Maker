import logging.config

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from trader.exchange.abstract_book import AbstractBook
from trader.database.models.order import Order
import config
from trader.database.models.base_wrapper import BaseWrapper

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


@AbstractBook.register
class Book(BaseWrapper):

  pair = Column("pair", String(15))
  orders = relationship("Order", lazy="dynamic", collection_class=list,
                        cascade="all, delete-orphan")

  def __init__(self, pair):

    self.pair = pair
    self.persist = True

  def add_order_to_book(self, order):
    if not isinstance(order, Order):
      raise TypeError(
        "Expected order to be of type Order, but received type {}", type(order)
      )
    self.orders.append(order)

  def get_all_orders(self):
    return self.orders.all()

  def get_ready_orders(self):
    return self.orders.filter(
      Order._status == "ready").all()

  def get_open_orders(self):
    return self.orders.filter(
      Order._status == "open").all()

  def get_filled_orders(self):
    return self.orders.filter(
      Order._status == "filled").all()

  def get_canceled_orders(self):
    return self.orders.filter(
      Order._status == "canceled").all()

  def get_rejected_orders(self):
    return self.orders.filter(
      Order._status == "rejected").all()

  def order_filled(self, filled_order):
    logger.debug("Updating filled order: {}".format(filled_order))
    filled_order.status = "filled"
    filled_order.filled = filled_order.size

  def __repr__(self):
    return "<Book id:{} pair:{}, order count:{}>".format(
      self.id, self.pair, len(self.get_open_orders())
    )


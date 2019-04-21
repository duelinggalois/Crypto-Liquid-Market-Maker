import logging
import logging.config

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from . import trading
from .order import Order
import config
from ..database.manager import BaseWrapper

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class Book(BaseWrapper):

  pair = Column("pair", String(15))
  orders = relationship(Order, lazy="dynamic", collection_class=set)

  def __init__(self, pair, persist=True, test=True):

    self.pair = pair
    self.ready_orders = []
    self.open_orders = []
    self.filled_orders = []
    self.canceled_orders = []
    self.persist = persist
    self.test = test
    logger.debug("Book.test: {}".format(self.test))
    if persist:
      self.save()

  def add_order(self, side, size, price, post_only=True):
    order = Order(
      self.pair, side, size, price, post_only=post_only,
      persist=self.persist, test=self.test
    )
    self.ready_orders.append(order)
    if self.persist:
      order.save()

  def send_orders(self):
    buys = [o for o in self.ready_orders if o.side == "buy"]
    sells = [o for o in self.ready_orders if o.side == "sell"]
    pick_sell = True
    while len(self.ready_orders) > 0:
      if pick_sell and len(sells) > 0:
        order = sells.pop(0)
        if len(buys) != 0:
          pick_sell = False
      else:
        order = buys.pop(0)
        if len(sells) != 0:
          pick_sell = True
      self.ready_orders.remove(order)
      trading.send_order(order)
      order.status = "pending"
      trading.confirm_order(order)
      order.status = "open"
      self.open_orders.append(order)
      if self.persist:
        order.save()


  def cancel_all_orders(self):
    self.cancel_order_list(self.open_orders)

  def cancel_order_list(self, order_list):
    while len(self.open_orders) > 0:
      order = self.open_orders.pop()
      trading.cancel_order(order)
      order.status = "canceled"
      self.canceled_orders.append(order)
      if self.persist:
        order.save()

  def order_filled(self, filled_order):
    logger.debug("Updating filled order: {}".format(filled_order))

    self.open_orders.remove(filled_order)
    self.filled_orders.append(filled_order)

    filled_order.status = "filled"
    if self.persist:
      filled_order.save()
      filled_order.session.commit()

    return filled_order

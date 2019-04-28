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
  orders = relationship("Order", lazy="dynamic", collection_class=list)

  def __init__(self, pair, persist=True, test=True):

    self.pair = pair
    self.ready_orders = []
    self.open_orders = []
    self.filled_orders = []
    self.canceled_orders = []
    self.rejected_orders = []
    self.persist = persist
    self.test = test
    logger.debug("Book.test: {}".format(self.test))
    if persist:
      self.save()

  def create_new_order(self, side, size, price, post_only=True):
    order = Order(
      self.pair, side, size, price, post_only=post_only,
      persist=self.persist, test=self.test
    )
    self.orders.append(order)
    return order

  def add_order(self, side, size, price, post_only=True):
    order = self.create_new_order(side, size, price, post_only=post_only)
    self.ready_orders.append(order)
    if self.persist:
      order.save()

  def add_and_send_order(self, side, size, price, post_only=True):
    order = self.create_new_order(side, size, price, post_only=post_only)
    self.send_order(order)

  def send_order(self, order):
    trading.send_order(order)
    order.status = "pending"
    trading.confirm_order(order)
    if order.status == "open":
      self.open_orders.append(order)
    elif order.status == "filled":
      self.filled_orders.append(order)
    elif order.status == "rejected":
      self.rejected_orders.append(order)
    else:
      logger.error("Received {} status when sending order:\n{}".format(
        order.status, order
      ))

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
      self.send_order(order)

  def cancel_all_orders(self):
    self.cancel_order_list(self.open_orders)

  def cancel_order_list(self, order_list):
    while len(order_list) > 0:
      order = order_list.pop()
      trading.cancel_order(order)
      order.status = "canceled"
      try:
        self.open_orders.remove(order)
      except ValueError:
        logger.info("Order not found in open orders: {}".format(
          order
        ))

      self.canceled_orders.append(order)
      if self.persist:
        order.save()

  def cancel_order(self, side, price):
    try:
      order_to_cancel = next(
        o for o in self.open_orders if o.side == side and o.price == price)
      trading.cancel_order(order_to_cancel)
      self.open_orders.remove(order_to_cancel)
      self.canceled_orders.append(order_to_cancel)
    except StopIteration:
      logger.warn("Could not find {} order at price {} to cancel".format(
        side, price
      ))

  def order_filled(self, filled_order):
    logger.debug("Updating filled order: {}".format(filled_order))

    self.open_orders.remove(filled_order)
    self.filled_orders.append(filled_order)

    filled_order.status = "filled"
    if self.persist:
      filled_order.save()
      filled_order.session.commit()

    return filled_order

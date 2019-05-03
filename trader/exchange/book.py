import logging
import logging.config
from decimal import Decimal
from pprint import pformat

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

  def add_and_send_order(self, side, size, price, post_only=True):
    order = self.create_new_order(side, size, price, post_only=post_only)
    # Recursion may override this order
    order = self.send_order(order)
    return order

  def send_order(self, order):
    trading.send_order(order)
    if order.status == "rejected":
      if order.post_only and order.reject_reason == "post only":
        self.rejected_orders.append(order)
        # Find first price available for post-only
        logger.warn("Post-only rejected:\n" + pformat(str(order)))
        # Recursive loop override rejected order, confirm happens in recursion
        return self.post_at_best_post_only(order.side, order.size)
      else:
        logger.error("Exchange rejected order for the following reason: {}"
                     .format(order.rejected_reason))
    trading.confirm_order(order)
    if order.status == "open":
      self.open_orders.append(order)
    elif order.status == "filled":
      self.filled_orders.append(order)
    else:
      logger.error("Received {} status when sending order:\n".format(
        order.status) + pformat(order)
      )

    if self.persist:
        order.save()
    return order

  def post_at_best_post_only(self, side, size):
    # if we are buying we want minus, if we are selling we want plus
    details = trading.get_product(self.pair, test=self.test)
    plus_or_minus = -1 if side == "buy" else 1
    adjust = plus_or_minus * Decimal(details["quote_increment"])
    ask, bid = trading.get_first_book(self.pair, test=self.test)
    price = (Decimal(ask[0][0]) + adjust if side == "buy" else
             Decimal(bid[0][0]) + adjust)
    # recursive loop
    return self.add_and_send_order(side, size, price)

  def cancel_all_orders(self):
    self.cancel_order_list(self.open_orders)

  def cancel_order_list(self, order_list):
    while len(order_list) > 0:
      order = order_list.pop()
      self.trading_cancel_order(order)
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

  def cancel_order_by_attribute(self, side, size):
    """
    Cancels order of matching side and size. When more than one, the oldest
    order will be canceled.
    """
    matched_orders = [
      o for o in self.open_orders if o.side == side and o.size == size
    ]
    if len(matched_orders) >= 1:
      # Grab the the first posted trade in the case there is more than one
      order_to_cancel = matched_orders[0]
      logging.debug("Found order to cancel {}".format(order_to_cancel.id))
      self.trading_cancel_order(order_to_cancel)
      self.open_orders.remove(order_to_cancel)
      self.canceled_orders.append(order_to_cancel)
    else:
      logger.error("could not find order on {} side and {} size"
                   .format(side, size))

  def order_filled(self, filled_order):
    logger.debug("Updating filled order: {}".format(filled_order))

    self.open_orders.remove(filled_order)
    self.filled_orders.append(filled_order)

    filled_order.status = "filled"
    if self.persist:
      filled_order.save()
      filled_order.session.commit()

    return filled_order

  def trading_cancel_order(self, order):
    trading.cancel_order(order)

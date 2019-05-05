import uuid
from decimal import Decimal

from trader.exchange.abstract_book import AbstractBook


class NoopBook(AbstractBook):

  def __init__(self, pair="BTC-USD", mid_market=Decimal("500") ):
    self.pair = pair
    self.orders = []

  def add_order_to_book(self, order):
   self.orders.append(order)

  def get_open_orders(self):
    return [o for o in self.orders if o.status == "open"]

  def get_ready_orders(self):
    return [o for o in self.orders if o.status == "ready"]

  def get_filled_orders(self):
    return [o for o in self.orders if o.status == "filled"]

  def get_canceled_orders(self):
    return  [o for o in self.orders if o.status == "canceled"]

  def get_rejected_orders(self):
    return  [o for o in self.orders if o.status == "rejected"]

  def order_filled(self, filled_order):
    filled_order.status = "filled"

  def get_all_orders(self):
    return self.ready_orders.extend(self.open_orders).extend(self.filled_orders).extend(self.rejected_orders)

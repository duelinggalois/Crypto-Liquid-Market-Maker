from . import trading
from .order import Order


class Book():

  def __init__(self, pair, test=False):

    self.pair = pair
    self.unsent_orders = []
    self.open_orders = []
    self.filled_orders = []
    self.canceled_orders = []
    self.test = test

  def add_order(self, side, size, price):
    self.unsent_orders.append(
        Order(self.pair, side, size, price, test=self.test))

  def send_orders(self):
    for order in self.unsent_orders:
      trading.send_order(order)
      self.open_orders.append(order)
    self.unsent_orders = []

  def cancel_all_orders(self):
    self.cancel_order_list(self.open_orders)

  def cancel_order_list(self, order_list):
    for order in order_list:
      trading.cancel_order(order)
      self.canceled_orders.append(order)
    self.open_orders = [o for o in self.open_orders if o not in order_list]

  def order_filled(self, order_id):
    filled_order = [
      order for order in self.open_orders if order.id == order_id
    ][0]
    self.open_orders.remove(filled_order)
    self.filled_orders.append(filled_order)
    return filled_order

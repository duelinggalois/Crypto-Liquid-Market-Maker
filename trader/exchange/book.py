import logging
import logging.config

from . import trading
from .order import Order
import config

from ..database.manager import BaseWrapper, Engine, Test_Engine

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class Book():

  def __init__(self, pair, persist=True, test=True):

    self.pair = pair
    self.unsent_orders = []
    self.open_orders = []
    self.filled_orders = []
    self.canceled_orders = []
    self.persist = persist
    self.test = test
    logger.debug("Book.test: {}".format(self.test))

    # Temporary home for table creation
    if test:
      BaseWrapper.metadata.create_all(Test_Engine)
    else:
      BaseWrapper.metadata.create_all(Engine)

  def add_order(self, side, size, price, post_only=True):
    order = Order(
      self.pair, side, size, price, post_only=post_only,
      persist=self.persist, test=self.test
    )
    order.save()
    self.unsent_orders.append(order)

  def send_orders(self):
    for order in self.unsent_orders:
      trading.send_order(order)
      trading.confirm_order(order.exchange_id)
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
    filled_order = next(
      order for order in self.open_orders if order.exchange_id == order_id
    )
    self.open_orders.remove(filled_order)
    self.filled_orders.append(filled_order)

    filled_order.status = "filled"
    if self.persist:
      filled_order.save()
      filled_order.session.commit()

    return filled_order

import abc


class AbstractBook(abc.ABC):

  @abc.abstractmethod
  def add_order_to_book(self, order):
    pass

  @abc.abstractmethod
  def get_all_orders(self):
    pass

  @abc.abstractmethod
  def get_ready_orders(self):
    pass

  @abc.abstractmethod
  def get_open_orders(self):
    pass

  @abc.abstractmethod
  def get_filled_orders(self):
    pass

  @abc.abstractmethod
  def get_canceled_orders(self):
    pass

  @abc.abstractmethod
  def get_rejected_orders(self):
    pass

  @abc.abstractmethod
  def order_filled(self, filled_order):
    pass

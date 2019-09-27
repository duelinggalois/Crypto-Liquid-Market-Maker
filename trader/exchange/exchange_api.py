import abc


class ExchangeApi(abc.ABC):
  """Abstract class for implementing a wrapper for a specific exchange api."""

  url = None
  auth = None
  type = None
  enum = None

  @staticmethod
  @abc.abstractmethod
  def send_order(order):
    """Sends an order to exchange based on content of Order object. Exchange returns
    a status of pending and requires to poll the api to confirm order is open.
    this can be done with the confirm_order function.
    """
    pass

  @staticmethod
  @abc.abstractmethod
  def confirm_order(order):
    """Verify status is no longer pending after order is sent.
    """
    pass

  @staticmethod
  @abc.abstractmethod
  def cancel_order(order):
    """cancel order
    """
    pass

  @staticmethod
  @abc.abstractmethod
  def cancel_order_by_id(id):
    """cancel an order without the order object using the order id"""
    pass

  @staticmethod
  @abc.abstractmethod
  def get_book(pair, level):
    """Get book for given pair"""
    pass

  @staticmethod
  @abc.abstractmethod
  def get_mid_market_price(pair):
    """retrieve average of best bid and ask"""
    pass

  @staticmethod
  @abc.abstractmethod
  def get_first_book(pair):
    """find first trades in book for given pair."""
    pass

  @staticmethod
  @abc.abstractmethod
  def get_open_orders(pair=None):
    """get_open_orders on exchange"""
    pass

  @staticmethod
  @abc.abstractmethod
  def order_status(exchange_id):
    """Ask exchange for status on order_id."""
    pass

  @staticmethod
  @abc.abstractmethod
  def get_products():
    """Get exchange products."""
    pass

  @staticmethod
  @abc.abstractmethod
  def get_product_details(pair):
    """Get product details"""
    pass

  def __str__(self):
    return "<{} url: {}>".format(self.__class__.__name__, self.url)

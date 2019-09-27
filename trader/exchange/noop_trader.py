import uuid

from trader.exchange.api_enum import ApiEnum
from trader.exchange.exchange_api import ExchangeApi


class NoopApi(ExchangeApi):
  enum = ApiEnum.NoopApi
  test = True
  pairs = ("BTC-USD", "ETH_USD", "ETH-BTC")
  mid_market_prices = {
    "BTC-USD": "1000",
    "ETH_USD": "200",
    "ETH-BTC": ".03"
  }

  @classmethod
  def set_noop_parameters(cls, mid_market_prices, pairs):
    if pairs is None:
      cls.pairs =  pairs
    if mid_market_prices is None:
      mid_market_prices = mid_market_prices
    cls.mid_market_prices = {
      key: mid_market_prices[pairs.index(key)] for key in pairs
    }

  @classmethod
  def reset_noop(cls):
    cls.set_noop_parameters(("1000", "200", ".03"),
                            ("BTC-USD", "ETH_USD", "ETH-BTC"))

  @staticmethod
  def send_order(order):
    order.status = "pending"
    order.exchange_id = str(uuid.uuid4())

  @staticmethod
  def confirm_order(order):
    order.status = "open"

  @staticmethod
  def cancel_order(order):
    order.status = "canceled"

  @staticmethod
  def cancel_order_by_id(id):
    pass

  @staticmethod
  def get_book(pair, level):
    pass

  @classmethod
  def get_mid_market_price(cls, pair):
    return cls.mid_market_prices[pair]

  @staticmethod
  def get_first_book(pair):
    pass

  @staticmethod
  def get_open_orders(pair=None):
    pass

  @staticmethod
  def order_status(exchange_id):
    pass

  @staticmethod
  def get_products(test=True):
    return ["BTC-USD", "ETH-USD", "ETH-BTC"]

  @staticmethod
  def get_product_details(pair):
    """returns dictionary with the following keys.
    'id', 'base_currency', 'quote_currency', 'base_min_size', 'base_max_size',
    'quote_increment', 'display_name', 'status', 'margin_enabled',
    'status_message', 'min_market_funds', 'max_market_funds', 'post_only',
    'limit_only', 'cancel_only'
    :param pair:
    :return: exchange details for pair
    """
    if pair == "BTC-USD":
      return {
        'id': 'BTC-USD',
        'base_currency': 'BTC',
        'quote_currency': 'USD',
        'base_min_size': '0.00100000',
        'base_max_size': '280.00000000',
        'quote_increment': '0.01000000',
        'base_increment': '0.00000001',
        'display_name': 'BTC/USD',
        'min_market_funds': '10',
        'max_market_funds': '1000000',
        'margin_enabled': False,
        'post_only': False,
        'limit_only': False,
        'cancel_only': False,
        'status': 'online',
        'status_message': ''
      }
    if pair == "ETH-USD":
      return {
        'id': 'ETH-USD',
        'base_currency': 'ETH',
        'quote_currency': 'USD',
        'base_min_size': '0.01000000',
        'base_max_size': '2800.00000000',
        'quote_increment': '0.01000000',
        'base_increment': '0.00000001',
        'display_name': 'ETH/USD',
        'min_market_funds': '10',
        'max_market_funds': '1000000',
        'margin_enabled': False,
        'post_only': False,
        'limit_only': False,
        'cancel_only': False,
        'status': 'online',
        'status_message': ''
      }
    if pair == "ETH-BTC":
      return {
        'id': 'ETH-BTC',
        'base_currency': 'ETH',
        'quote_currency': 'BTC',
        'base_min_size': '0.01000000',
        'base_max_size': '2400.00000000',
        'quote_increment': '0.00001000',
        'base_increment': '0.00000001',
        'display_name': 'ETH/BTC',
        'min_market_funds': '0.001',
        'max_market_funds': '80',
        'margin_enabled': False,
        'post_only': False,
        'limit_only': False,
        'cancel_only': False,
        'status': 'online',
        'status_message': ''
      }
    return None

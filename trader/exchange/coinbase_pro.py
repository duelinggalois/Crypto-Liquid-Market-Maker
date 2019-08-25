import config
import logging.config
from decimal import Decimal
from pprint import pformat
import requests

from trader.exchange import cb_authorize
from trader.exchange.api_enum import ApiEnum
from trader.exchange.exchange_api import ExchangeApi

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class CoinbaseProBase(ExchangeApi):

  def send_order(self, order):
    """Sends an order to exchange based on content of Order object. Exchange returns
    a status of pending and requires to poll the api to confirm order is open.
    this can be done with the confirm_order function.
    """
    json_order = {
      "size": str(order.size),
      "price": str(order.price),
      "side": order.side,
      "product_id": order.pair,
      "post_only": order.post_only
    }
    logger.debug("sent order:\n{}".format(pformat(json_order)))
    order_post = requests.post(
      self.url + 'orders',
      json=json_order,
      auth=self.auth
    )
    response = order_post.json()
    logger.debug("response:\n{}".format(pformat(response)))
    if "message" not in response:
      # order.responses.append(response)
      order.exchange_id = response["id"]
      order.status = response["status"]
      if response["status"] == "rejected":
        order.reject_reason = response["reject_reason"]

      # order.update_history(response["status"])
      logger.info("Order Posted: {} {} {} {} {}".format(
        response["product_id"],
        response["side"],
        response["size"],
        response["price"],
        response["id"]
      ))

    else:
      logger.error("API sent message: {}\n{}".format(
        response["message"],
        str(order)
      ))
    order.response = response

  def confirm_order(self, order):
    response = self.order_status(order.exchange_id)
    if response != "Error" and "message" not in response:
      order.status = (response["status"] if response["status"] != "done" else
                      response["done_reason"]
                      )
      order.filled = response["filled_size"]
    else:
      order.status = "Error"

  def cancel_order(self, order):
    message = self.cancel_order_by_id(order.exchange_id)

    if order.exchange_id in message:
      order.status = "canceled"
      logger.info("Order Deleted with id:" + str(message))

    elif "message" in message:
      log_message = "When deleting order id {} received message: {}".format(
            str(order.exchange_id),
            message["message"]
      )
      if message["message"].lower() in (
        "order not found", "order already done"):
        logger.warning(log_message)
      else:
        # Unknown error
        logger.error(log_message)

    else:
      logger.error(
        ("Order id was found before deleting but was found in delete response: "
         "{}").format(str(order.exchange_id)))

    return message

  def cancel_order_by_id(self, id):
    order_delete = requests.delete(self.url + "orders/" + id, auth=self.auth)
    response = order_delete.json()
    logger.debug("Response: " + str(response))
    return response

  def get_book(self, pair, level):
    """Get book for given pair
    return {
      "operations": "3",
      "bids": [
          [ price, size, num-orders ],
          [ "295.96", "4.39088265", 2 ],
          ...
      ],
      "asks": [
          [ price, size, num-orders ],
          [ "295.97", "25.23542881", 12 ],
          ...
      ]
    }
    """
    book = requests.get(
      self.url + "products/" + pair + "/book",
      auth=self.auth)

    return book.json()

  def get_mid_market_price(self, pair):
    ask, bid = self.get_first_book(pair)
    return (Decimal(ask[0][0]) + Decimal(bid[0][0])) / 2

  def get_first_book(self, pair):
    """
    find first trades in book for given pair.

    return ([['7239.99', '0.7567461', 1]], [['7239.98', '9.11000002', 5]])
    """
    book = self.get_book(pair, 1)
    logger.debug(pformat(book))
    return book["asks"], book["bids"]

  def get_open_orders(self, pair=None):
    """this method is limited by the api and will only return 100 orders"""
    if pair is None:
      query_params = "?status=open"
    else:
      query_params = "?status=open&product_id=" + pair

    get_orders = requests.get(self.url + "orders" + query_params, auth=self.auth)
    return get_orders.json()

  def order_status(self, exchange_id):
    """Ask exchange for status on order_id.
      returns dictionary with following keys:
      ['id', 'price', 'size', 'product_id', 'side', 'type', 'time_in_force',
      'post_only', 'created_at', 'fill_fees', 'filled_size', 'executed_value',
      'status', 'settled']
      if canceled may return 404 or dictionary with "message" of None.
      if bad format, will return "message" if Invalid order id
      """
    response = requests.get(self.url + "orders/" + exchange_id, auth=self.auth)
    logger.debug("response: \n" + pformat(response.json()))
    if not response.ok:
      if "message" in response.json():
        logger.error((
          "Bad response for exchange_id: {} message: {} reason: {} "
          "status code: {}"
        ).format(
          exchange_id, response.json()["message"], response.reason,
          response.status_code
        ))
        return response.json()
      else:
        logger.error((
          "Bad response for exchange_id: {}  reason: {} status code: {}"
        ).format(
          exchange_id, response.reason,
          response.status_code
        ))
        return "Error"
    return response.json()

  def get_products(self):
    response = requests.get(self.url + "products")
    product_ids = [product['id'] for product in response.json()]
    product_ids.sort()
    return product_ids

  def get_product_details(self, pair):
    """Get product details.

    returns dictionary with the following keys.
    {
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

    """
    response = requests.get(self.url + "products/" + pair)
    return response.json()


class CoinbasePro(CoinbaseProBase):
  enum = ApiEnum.CoinbasePro

  def __init__(self):
    self.url = config.rest_api_url
    self.auth = cb_authorize.run_coinbase_pro_auth()


class CoinbaseProTest(CoinbaseProBase):
  enum = ApiEnum.CoinbaseProTest

  def __init__(self):
    self.url = config.test_rest_api_url
    self.auth = cb_authorize.test_run_coinbase_pro_auth()

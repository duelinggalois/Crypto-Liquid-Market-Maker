import logging
import logging.config
from decimal import Decimal
from pprint import pformat

from . import authorize
import requests
import config


logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


def send_order(Order):
  logging.debug("Order.test: {}".format(Order.test))
  url, auth = get_url_auth(Order.test)

  json_order = {
    "size": str(Order.size),
    "price": str(Order.price),
    "side": Order.side,
    "product_id": Order.pair,
    "post_only": Order.post_only
  }
  logger.debug("sent order:\n" + pformat(json_order))
  order_post = requests.post(
    url + 'orders',
    json=json_order,
    auth=auth
  )
  response = order_post.json()
  logger.debug("response: " + pformat(response))
  if "message" not in response:
    Order.responses.append(response)
    Order.exchange_id = response["id"]
    Order.status = response["status"]
    if Order.persist:
      Order.save()

    Order.update_history(response["status"])
    logger.info("Order Posted: {} {} {} {}".format(
      response["product_id"],
      response["side"],
      response["size"],
      response["price"]
    ))

  else:
    Order.update_history(response["message"])
    logger.error("API sent message: {}\n{}".format(
      response["message"],
      str(Order)
    ))


def cancel_order(Order):
  message = cancel_order_by_id(Order.exchange_id, test=Order.test)

  if Order.exchange_id in message:
    Order.status = "canceled"
    logger.info("Order Deleted with id:" + str(message))

  elif "message" in message:
    Order.responses.append(message["message"])
    Order.update_history("Error deleting order")
    Order.status = "error"

    logger.error(
      "When deleting order recieved message: {}\n{}".format(
        message["message"],
        str(Order)
      )
    )

  else:
    logger.error(
        ("Order id was found before deleting but was found in delete response"
         " \n{}")
        .format(str(Order)))

  if Order.persist:
    Order.session.commit()

  return message


# DOES NOT UPDATE DATABASE
def cancel_order_by_id(id, test=False):

  url, auth = get_url_auth(test)

  order_delete = requests.delete(url + "orders/" + id, auth=auth)
  response = order_delete.json()
  logger.debug("Response: " + str(response))
  return response


def get_book(pair, level, test=False):

  url, auth = get_url_auth(test)

  get_book = requests.get(
    url + "products/" + pair + "/book",
    auth=auth)

  return get_book.json()


def get_mid_market_price(pair, test=False):
  book = get_book(pair, 1, test=test)
  logger.debug(pformat(book))
  ask = Decimal(book["asks"][0][0])
  bid = Decimal(book["bids"][0][0])
  return (ask + bid) / 2


def get_open_orders(pair=None, test=True):
  '''this method is limited by the api and will only return 100 orders
  '''
  url, auth = get_url_auth(test)
  if pair is None:
    query_params = "?status=open"
  else:
    query_params = "?status=open&product_id=" + pair

  get_orders = requests.get(url + "orders" + query_params, auth=auth)
  return get_orders.json()


def order_status(exchange_id, test=True):
  '''Ask exchange for status on order_id.
  returns dictionary with following keys:
  ['id', 'price', 'size', 'product_id', 'side', 'type', 'time_in_force',
  'post_only', 'created_at', 'fill_fees', 'filled_size', 'executed_value',
  'status', 'settled']
  if canceled may return 404 or dictonary with "message" of None.
  if bad format, will return "message" if Invalid order id
  '''
  url, auth = get_url_auth(test)
  response = requests.get(url + "orders/" + exchange_id, auth=auth)
  return response.json()


def get_products(test=True):
  url, auth = get_url_auth(test)
  response = requests.get(url + "products")
  product_ids = [product['id'] for product in response.json()]
  product_ids.sort()
  return product_ids


def get_url_auth(test):
  if test:
    url = config.test_rest_api_url
    auth = authorize.test_run_coinbase_pro_auth()
  else:
    url = config.rest_api_url
    auth = authorize.run_coinbase_pro_auth()
  return url, auth

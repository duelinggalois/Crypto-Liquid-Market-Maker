from . import authorize
import requests
import config
import logging


logging.basicConfig(filename='info.log', level=logging.INFO)


def send_order(Order):
  if Order.test:
    url = config.test_rest_api_url
    auth = authorize.test_run_coinbase_pro_auth()
  else:
    url = config.rest_api_url
    auth = authorize.run_coinbase_pro_auth()

  json_order = {
    "size": str(Order.size),
    "price": str(Order.price),
    "side": Order.side,
    "product_id": Order.pair,
    "post_only": Order.post_only
  }

  order_post = requests.post(
    url + 'orders',
    json=json_order,
    auth=auth
  )

  response = order_post.json()

  if "message" not in response:
    Order.responses.append(response)
    Order.id = response["id"]
    Order.update_history(response["status"])
    logging.info("Order Posted:" + str(order_post.json()))

  else:
    Order.update_history(response["message"])
    logging.error("API sent message: " + response["message"])


def cancel_order(Order):
  if Order.test:
    url = config.test_rest_api_url
    auth = authorize.test_run_coinbase_pro_auth()
  else:
    url = config.rest_api_url
    auth = authorize.run_coinbase_pro_auth()

  order_delete = requests.delete(url + "orders/" + Order.id, auth=auth)
  response = order_delete.json()
  logging.debug("Response: " + str(response))

  if Order.id in response:
    Order.responses.append({"deleted": response})
    Order.update_history("deleted")
    logging.info("Order Deleted with id:" + str(response))
  elif "message" in response:
    Order.responses.append(response["message"])
    Order.update_history("Error deleting order")
    logging.error(
      "When deleting order recieved message: " + response["message"])
  else:
    logging.error(
        "Order id was found before deleting but was found in delete response")
    this = 2 + 2


def get_book(pair, level, test=False):
  if test:
    url = config.test_rest_api_url
    auth = authorize.test_run_coinbase_pro_auth()
  else:
    url = config.rest_api_url
    auth = authorize.run_coinbase_pro_auth()

  get_book = requests.get(
    url + "products/" + pair + "/book",
    auth=auth)

  return get_book.json()


def get_mid_market_price(pair, test=False):
  book = get_book(pair, 1, test=test)
  ask = float(book["asks"][0][0])
  bid = float(book["bids"][0][0])
  return (ask + bid) / 2


def get_open_orders(pair=None, test=False):
  if test:
    url = config.test_rest_api_url
    auth = authorize.test_run_coinbase_pro_auth()
  else:
    url = config.rest_api_url
    auth = authorize.run_coinbase_pro_auth()
  if pair is None:
    query_params = "?status=open"
  else:
    query_params = "?status=open&product_id=" + pair

  get_orders = requests.get(url + "orders" + query_params, auth=auth)
  return get_orders.json()

import json
import logging.config

import config
from trader.socket.thread_handler import ThreadHandler

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class Reader:

  def __init__(self, BookManagerMaker):
    self.thread_handler = ThreadHandler(BookManagerMaker)
    self._sell_thread = None
    self._buy_thread = None
    self.first_subscribe = True
    self.send_trades = False

  def new(self, msg):
    """Choose which process function to use to process message based on
    message type.
    """
    chooser = {
      "subscriptions": self.subscriptions,
      "last_match": self.last_match,
      "match": self.match,
      "error": self.error
    }
    function_name = chooser.get(msg["type"], self.other)
    return function_name(msg)

  def subscriptions(self, msg):
    """Channels:
      {'channels': [{'product_ids': ['ETH-BTC'], 'name': 'matches'}],
       'type': 'subscriptions'}
    Pair:
    """
    logger.info("Subscribed")
    for c in msg["channels"]:
      logger.info("Channel: {} \tPair: {}".format(c['name'],
                                                  c['product_ids']))

  def last_match(self, msg):
    logger.info("Last Match")
    logger.info("< {0} - {1} - trade id: {2} - "
                "side: {3} size: {4} price: {5}".format(
                  msg["time"],
                  msg["product_id"],
                  msg["trade_id"],
                  msg["side"],
                  msg["size"],
                  msg["price"]
                ))
    if self.first_subscribe:
      self.thread_handler.start_initial_trade_thread()
      self.first_subscribe = False
    else:
      self.check_book(msg)

  def match(self, msg):
    """Processes match messages from the socket
    :param msg: json in the form:
      {
          "type": "match",
          "trade_id": 10,
          "sequence": 50,
          "maker_order_id": "ac928c66-ca53-498f-9c13-a110027a60e8",
          "taker_order_id": "132fb6ae-456b-4654-b4e0-d681ac05cea1",
          "time": "2014-11-07T08:19:27.028459Z",
          "product_id": "BTC-USD",
          "size": "5.23512",
          "price": "400.23",
          "side": "sell"
      }
    :return: none
    """
    logger.info("< {0} - {1} - trade_id: {2} - "
                "side: {3} size: {4} price: {5}".format(
                  msg["time"],
                  msg["product_id"],
                  msg["trade_id"],
                  msg["side"],
                  msg["size"],
                  msg["price"]
                )
                )
    self.check_book(msg)

  @staticmethod
  def error(msg):
    logger.exception("< {} message: {}".format(
      msg["error"],
      msg[""]
    )
    )
    raise ValueError(msg["error"])

  @staticmethod
  def other(msg):
    load_msg = json.loads(msg)
    statement = "< "
    for i in load_msg.keys():
      statement += '"' + i + '"' + '"' + str(load_msg[i]) + '"' + ", "
    logger.info(statement[:-2])

  def check_book(self, msg):
    self.thread_handler.check_book_for_match(msg)


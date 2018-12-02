import json
import logging
import logging.config

import config

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class Reader():

  def __init__(self, book_manager):
    self.book_manager = book_manager

  def new(self, msg):
    '''Chooose which process function to use to process message based on
    message type.
    '''
    chooser = {
      "subscriptions": self.subscriptions,
      "last_match": self.last_match,
      "match": self.match,
      "error": self.error
    }
    function_name = chooser.get(msg["type"], self.other)
    return function_name(msg)

  def subscriptions(self, msg):
    '''Channels:
      {'channels': [{'product_ids': ['ETH-BTC'], 'name': 'matches'}],
       'type': 'subscriptions'}
    Pair:
    '''
    logger.info("Subscribed")
    for c in msg["channels"]:
      logger.info(f"Channel: {c['name']}\t\tPair: {c['product_ids']}")

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
                )
                )

  def match(self, msg):
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
    self.book_manager.check_match(msg)

  def error(self, msg):
    logger.exception("< {} message: {}".format(
      msg["error"],
      msg[""]
    )
    )
    raise ValueError(msg["error"])

  def other(self, msg):
    load_msg = json.loads(msg)
    statement = "< "
    for i in load_msg.keys():
      statement += '"' + i + '"' + '"' + str(load_msg[i]) + '"' + ", "
    logger.info(statement[:-2])

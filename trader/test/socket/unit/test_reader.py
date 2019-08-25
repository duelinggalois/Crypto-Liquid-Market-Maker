import unittest
from queue import Queue

from trader.database.models.trading_terms import TradingTerms
from trader.socket.reader import Reader
from trader.socket.thread_handler import AbstractThreadHandler

SUBSCRIBE_MSG = {'type': 'subscriptions',
                 'channels': [{'name': 'matches',
                               'product_ids': ['BTC-USD']}]}
LAST_MATCH_MSG = {'type': 'last_match',
                  'trade_id': 73580645,
                  'maker_order_id': 'cdf7456c-102f-43db-bb65-1831d74a0e2f',
                  'taker_order_id': '965e1ff9-3d20-48b8-867b-31d166d0024d',
                  'side': 'sell',
                  'size': '0.00236300',
                  'price': '10588.84000000',
                  'product_id': 'BTC-USD',
                  'sequence': 10782639422,
                  'time': '2019-09-06T01:26:54.341Z'}
MATCH_MSG_1 = {'type': 'match',
               'trade_id': 73580646,
               'maker_order_id': 'd3154d12-1a25-410b-8425-47f51b59b188',
               'taker_order_id': 'ea4938b7-d001-4ee7-9cf6-22eb6ca9ed3e',
               'side': 'sell',
               'size': '0.00615737',
               'price': '10588.81',
               'product_id': 'BTC-USD',
               'sequence': 10782639569,
               'time': '2019-09-06T01:26:59.664Z'}

MATCH_MSG_2 = {'type': 'match',
               'trade_id': 73580647,
               'maker_order_id': 'dc4cdef6-bbfe-4579-94ab-6f91f603bfb3',
               'taker_order_id': '796f5c25-24ce-41d0-b633-7dae77d8af7f',
               'side': 'sell',
               'size': '0.01988012',
               'price': '10588.80000000',
               'product_id': 'BTC-USD',
               'sequence': 10782639584,
               'time': '2019-09-06T01:27:00.478Z'}


class TestReader(unittest.TestCase):

  def setUp(self):
    self.maxDiff = None
    self.test_queue = Queue()
    self.thread_handler = NoopThreadHandler()
    self.reader = Reader(self.test_queue, thread_handler=self.thread_handler)

  def test_run(self):

    self.reader.start()

    self.test_queue.put(LAST_MATCH_MSG)
    self.test_queue.put(SUBSCRIBE_MSG)
    self.test_queue.put(MATCH_MSG_1)
    self.test_queue.put(MATCH_MSG_2)

    self.test_queue.join()
    self.reader.running = False

    self.reader.join()

    self.assertEqual(self.thread_handler.calls, [
      "handle_last_match_message({})".format(LAST_MATCH_MSG),
      "check_book_for_match({})".format(MATCH_MSG_1),
      "check_book_for_match({})".format(MATCH_MSG_2)
    ])


class NoopThreadHandler(AbstractThreadHandler):

  def __init__(self):
    self.calls = []

  def add_terms(self, terms: TradingTerms):
    self.calls.append("add_terms({})".format(terms))

  def remove_terms(self, terms: TradingTerms):
    self.calls.append("remove_terms({})".format(terms))

  def get_threads(self):
    self.calls.append("get_threads()")

  def check_book_for_match(self, message):
    self.calls.append("check_book_for_match({})".format(message))

  def handle_last_match_message(self, message):
    self.calls.append("handle_last_match_message({})".format(message))

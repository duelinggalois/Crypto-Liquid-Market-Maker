import time
import unittest

import config
from trader.socket.manager import SocketManager


class TestSocket(unittest.TestCase):

  def test_socket(self):
    try:
      start = time.time()

      sm = SocketManager(config.socket_url)
      sm.start()
      sm.add_subscription("BTC-USD", 'matches')

      # pause test till new match received
      while sm.socket_out.qsize() <= 3:
        if time.time() - start > 20:
          # fail test if it goes to long
          break
        time.sleep(.0001)

      sm.remove_subscription("BTC-USD", 'matches')
      messages = []
      while not sm.socket_out.empty():
        messages.append(sm.socket_out.get())
        sm.socket_out.task_done()
      # to avoid order issues, add all messages into a set and pull them out
      types = {m["type"] for m in messages}
      self.assertIn("last_match", types)
      self.assertIn("subscriptions", types)
      self.assertIn("match", types)

      last_match = next(m for m in messages if m['type'] == "last_match")
      subscription = next(m for m in messages if m['type'] == "subscriptions")
      match = next(m for m in messages if m['type'] == "last_match")
      self.assertEqual(last_match["product_id"], "BTC-USD")
      self.assertEqual(subscription["channels"], [{"name": "matches",
                                                  "product_ids": ["BTC-USD"]}])
      self.assertIn(match["side"], {"sell", "buy"})
      self.assertEqual(match["product_id"], "BTC-USD")
      sm.stop()
      self.assertFalse(sm.is_alive())
    finally:
      if sm.is_alive():
        sm.stop()

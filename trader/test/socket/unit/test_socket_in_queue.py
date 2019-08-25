import asyncio
import time
import unittest
from queue import Queue

from trader.socket.manager import SocketManagerAbstract
from trader.operations.socket_in_queue import SocketInQueue


class TestSocketInQueue(unittest.TestCase):

  def test_socket_in_queue(self):
    socket_in = SocketInQueue()
    socket_out = Queue()
    loop = asyncio.get_event_loop()
    socket_manager = NoopSocketManager('url',
                                       socket_in=socket_in,
                                       socket_out=socket_out,
                                       loop=loop)

    socket_in.put_message("subscribe", "BTC-USD", "match")
    socket_manager.start()
    time.sleep(.001)
    socket_in.put_message("subscribe", "LTC-USD", "match")
    time.sleep(.05)
    socket_in.put_stop_message()
    socket_in.join()
    socket_manager.join()
    messages = []
    while socket_out.qsize() > 0:
      messages.append(socket_out.get())
      socket_out.task_done()
    socket_out.join()
    # Order can vary, check that socket was able to consume messages and respond
    self.assertEqual(
      set(messages),
      {'{"type": "subscribe", "product_ids": ["BTC-USD"], "channels": '
       '["match"]}', '{"type": "subscribe", "product_ids": ["LTC-USD"], '
       '"channels": ["match"]}', ('BTC-USD', 1),
       ('BTC-USD', 2), ('BTC-USD', 3), ('BTC-USD', 4), ('BTC-USD', 5),
       ('BTC-USD', 6), ('BTC-USD', 7), ('BTC-USD', 8), ('BTC-USD', 9),
       ('BTC-USD', 10), ('BTC-USD', 11), ('BTC-USD', 12), ('BTC-USD', 13),
       ('BTC-USD', 14), ('BTC-USD', 15), ('BTC-USD', 16), ('BTC-USD', 17),
       ('BTC-USD', 18), ('BTC-USD', 19), ('BTC-USD', 20), ('LTC-USD', 1),
       ('LTC-USD', 2), ('LTC-USD', 3), ('LTC-USD', 4), ('LTC-USD', 5),
       ('LTC-USD',6), ('LTC-USD', 7), ('LTC-USD', 8), ('LTC-USD', 9),
       ('LTC-USD', 10), ('LTC-USD', 11), ('LTC-USD', 12), ('LTC-USD', 13),
       ('LTC-USD', 14), ('LTC-USD', 15), ('LTC-USD', 16), ('LTC-USD', 17),
       ('LTC-USD', 18), ('LTC-USD', 19), ('LTC-USD', 20)}
    )


class NoopSocketManager(SocketManagerAbstract):

  listening = True
  senders = []
  m = 0

  async def run_in_loop(self):
    while self.listening:
      await self.check_inbox()
      await self.listen()

  async def check_inbox(self):
    if not self.socket_in.empty():
      message = await self.socket_in.get_message()
      if message.action == "stop":
        self.listening = False
        return
      else:
        self.products.append(message.product_id)
        # add to socket_out for testing, normally sent to exchange.
        self.socket_out.put(message.get_json())
        self.senders.append(self.sender(message.product_id, 20))
    else:
      # This sleep allows the event loop to get control to allow for call_soon
      await asyncio.sleep(0)

  async def listen(self):
    message = await self.producer()
    if message is not None:
      self.socket_out.put(message)

  async def producer(self):
    while self.listening:
      if len(self.senders) > 0:
        if self.m >= len(self.senders):
          self.m = 0
        sender = self.senders[self.m]
        try:
          return await sender.__anext__()
        except StopAsyncIteration:
          self.senders.remove(sender)
          break
        finally:
          self.m += 1
          time.sleep(.00001)
      else:
        break

  async def sender(self, product, count_to):
    count = 1
    while self.listening and count <= count_to:
      yield (product, count)
      count += 1

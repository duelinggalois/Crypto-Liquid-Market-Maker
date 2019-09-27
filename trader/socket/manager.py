import abc
import asyncio
from queue import Queue
from threading import Thread

import config
import json
import logging.config
import time
import websockets

from trader.operations.socket_in_queue import SocketInQueue

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class SocketManagerAbstract(abc.ABC, Thread):

  listening = True
  products = []
  socket = None
  fast_error_count = 0

  def __init__(self, url, loop=None, socket_in=None, socket_out=None,
               api_key=None, api_secret=None, api_passphrase=None):
    self.url = url

    try:
      self.loop = asyncio.get_event_loop() if loop is None else loop
    except RuntimeError:
      asyncio.set_event_loop(asyncio.new_event_loop())
      self.loop = asyncio.get_event_loop()
    self.socket_in = SocketInQueue() if socket_in is None else socket_in
    self.socket_out = Queue() if socket_out is None else socket_out
    self.api_key = api_key
    self.api_secret = api_secret
    self.api_passphrase = api_passphrase
    super().__init__()

  def add_subscription(self, pair, subscription_type="matches"):
    self.socket_in.put_message("subscribe", pair, subscription_type)

  def remove_subscription(self, pair, subscription_type="matches"):
    self.socket_in.put_message("unsubscribe", pair, subscription_type)

  def run(self):
    self.loop.run_until_complete(self.run_in_loop())

  def stop(self):
    self.socket_in.put_stop_message()
    self.socket_in.join()
    self.socket_out.join()
    self.join()

  @abc.abstractmethod
  async def run_in_loop(self):
    raise NotImplementedError

  @abc.abstractmethod
  async def check_inbox(self):
    raise NotImplementedError

  @abc.abstractmethod
  async def listen(self):
    raise NotImplementedError


class SocketManager(SocketManagerAbstract):

  last_op = None
  repeat_error_count = 0
  subscriptions = []

  def run(self):
    self.last_op = time.time()
    logger.debug("starting socket")
    while self.listening:
      try:
        self.loop.run_until_complete(self.run_in_loop())
      except asyncio.TimeoutError:
        logger.warning("Ping Timeout, Restarting Web Socket")

      except websockets.exceptions.ConnectionClosed:
        logger.warning("Connection Closed, Restarting Web Socket")

      except websockets.InvalidStatusCode as e:
        logger.error("Might be getting rate limited")
        if self._last_op_stopwatch() < 3:
          self.fast_error_count += 1
        if self.fast_error_count > 5:
          raise e
        time.sleep(1)

      except Exception as e:
        logger.error("last message received {} seconds ago/n"
                     .format(self._last_op_stopwatch()))
        if self._last_op_stopwatch() < 3:
          self.fast_error_count += 1
        if self.fast_error_count > 5:
          logger.error("Too many repeated errors")
          raise e
        logger.warning("Restarting Web Socket")

  async def run_in_loop(self):
    logger.debug("starting loop")
    async with websockets.connect(self.url) as self.socket:
      await asyncio.gather(
        self._renew_subscriptions(),
        self.check_inbox(),
        self.listen()
      )

  async def _renew_subscriptions(self):
    for message in self.subscriptions:
      await self._send_to_socket(message)
      # rate limit
      await asyncio.sleep(.2)

  async def check_inbox(self):
    while self.listening:
      if not self.socket_in.empty():
        await self._process_inbox_message()
      else:
        await asyncio.sleep(1)

  async def listen(self):
    while self.listening:
      # Check socket message dequeue before trying to grab anything
      if len(self.socket.messages) <= 0:
        await asyncio.sleep(0.01)
      else:
        try:
          received = await self.socket.recv()
          message = json.loads(received)
          logger.debug("< {}".format(message))
          self.socket_out.put(message)
          self.repeat_error_count = 0
          self.last_op = time.time()

        except asyncio.TimeoutError:
          await self._ping_socket()

        except Exception as e:
          logger.exception("Socket had a unknown exception, last op received {}"
                           " seconds ago".format(self._last_op_stopwatch()))
          raise e

  async def _process_inbox_message(self):
    message = await self.socket_in.get_message()
    logger.info("pulled message from input queue: {}".format(message))
    if message.action == "stop":
      logger.warning("stopping socket manager")
      self.listening = False
      self.socket_out.put({"type": "stop"})
      self.socket_in.task_done()
      return await self.socket.close()
    if message.action == "subscribe":
      # store message for restarts
      self.subscriptions.append(message)
    if message.action == "unsubscribe":
      try:
        message_to_remove = next(
          m for m in self.subscriptions if m.product_id == message.product_id
          and m.channel == message.channel
        )
        self.subscriptions.remove(message_to_remove)
      except StopIteration:
        logger.warning(
          "could not this message in subscription list: {}".format(message)
        )
    logger.debug("sending message to socket")
    await self._send_to_socket(message)
    self.socket_in.task_done()

  async def _send_to_socket(self, message):
    logger.info("> {}".format(message))
    if message.authorize and self._has_api_keys():
      await self.socket.send(message.get_json_with_auth(
        self.api_key, self.api_secret, self.api_passphrase
      ))
    await self.socket.send(message.get_json())

  async def _ping_socket(self):
    logger.debug("> ping")
    await self.socket.ping()

  def _last_op_stopwatch(self):
    return time.time() - self.last_op

  def _has_api_keys(self):
    return (self.api_key is not None and self.api_passphrase is not None
            and self.api_secret is not None)

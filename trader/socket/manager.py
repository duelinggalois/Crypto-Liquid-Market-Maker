import asyncio
import base64
import config
import hashlib
import hmac
import json
import logging
import logging.config
import time
import traceback
from threading import Thread
import websockets


logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class SocketManager:

  def __init__(self, reader, BookManagerMaker,
               auth=False,
               url="",
               action='subscribe',
               product_ids=[],
               channel=["matches"],
               send_trades=False
               ):

    self.reader = reader
    self.auth = auth
    book_manager = BookManagerMaker()

    if url == "":
      if book_manager.is_trading_api_test():
        self.url = config.test_socket
      else:
        self.url = config.socket
    else:
      self.url = url
    logging.debug("SocketManager\n\ttest: {}\n\turl: {}\n\tpair: {}".format(
      book_manager.is_trading_api_test(), self.url, product_ids
    ))
    self.book_manager = book_manager
    self.channel = channel
    self.product_ids = product_ids
    if self.channel:
      self.sub_params = {
          'type': action,
          'product_ids': self.product_ids,
          'channels': ['matches']}
    else:
      self.sub_params = {
          'type': action,
          'product_ids': self.product_ids,
          'channels': self.channel
      }
    self.send_trades = send_trades
    self.protocol = ""
    self.last_time = time.time()
    self.api_key = None
    self.api_passphrase = None
    self.api_secret = None

  def auth_stamp(self):
    self.api_key = config.api_key
    self.api_secret = config.api_secret
    self.api_passphrase = config.api_passphrase
    timestamp = str(time.time())
    message = timestamp + 'GET' + '/users/self/verify'
    message = message.encode()
    hmac_key = base64.b64decode(self.api_secret)
    signature = hmac.new(hmac_key, message, hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest()).decode()
    self.sub_params['signature'] = signature_b64
    self.sub_params['key'] = self.api_key
    self.sub_params['passphrase'] = self.api_passphrase

  def run(self):
    if self.auth:
      self.auth_stamp()
    self.run = True
    loop = asyncio.get_event_loop()
    while self.run:
      try:
        loop.run_until_complete(self.connect())

      except asyncio.TimeoutError:
        logger.warning("Ping Timeout, Restarting Web Socket")

      except websockets.exceptions.ConnectionClosed:
        logger.warning("Connection Closed, Restarting Web Socket")

      except KeyboardInterrupt:
        logger.error("Keyboard Interruption, stopping socket")
        raise

      except Exception:
        logger.error("last message received {} seconds ago/n{}"
                     .format(self.last_time_watch(),
                             traceback.format_exc()))
        logger.warning("Restarting Web Socket")

  async def connect(self):
    self.last_time = time.time()
    async with websockets.connect(self.url) as self.ws:
      await self.send(json.dumps(self.sub_params))
      await self.listen()

  async def send(self, message):
    await self.ws.send(message)
    logger.info("> {}".format(message))

  async def listen(self):
    listen = True
    while listen:
      try:
        received = await asyncio.wait_for(self.ws.recv(), timeout=50)
        message = json.loads(received)
        logger.debug("< {}".format(message))
        self.reader.new(message)
        self.last_time = time.time()

      except asyncio.TimeoutError:
        await self.ping_socket()

      except websockets.exceptions.ConnectionClosed:
        logging.warn("Connection Closed Exception after {} seconds"
                     .format(round(self.last_time_watch(), 2)))
        raise websockets.exceptions.ConnectionClosed(
          1006, "1 minute without messages")

      except KeyboardInterrupt:
        raise

      except Exception:
        logger.exception("Socket had a general exception, last message "
                         "received {} seconds ago".format(
                            self.last_time_watch()
                         ))
        raise

  async def ping_socket(self):
    logger.debug("> ping")
    await self.ws.ping()

  def last_time_watch(self):
    return time.time() - self.last_time

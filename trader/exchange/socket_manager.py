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
import websockets


logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class SocketManager():

  def __init__(self,
               auth=False,
               url="",
               action='subscribe',
               product_ids=[],
               channel=[]
               ):

    self.auth = auth
    self.url = config.socket if url == "" else url
    self.channel = channel
    self.product_ids = product_ids
    if self.channel == []:
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
    self.protocol = ""

  def auth_stamp(self):
    self.api_key = config.api_key
    self.api_secretd = config.api_secret
    self.api_passphrase = config.api_pass
    timestamp = str(time.time())
    message = timestamp + 'GET' + '/users/self/verify'
    message = message.encode()
    hmac_key = base64.b64decode(self.api_secret)
    signature = hmac.new(hmac_key, message, hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest()).decode()
    self.sub_params['signature'] = signature_b64
    self.sub_params['key'] = self.api_key
    self.sub_params['passphrase'] = self.api_passphrase
    self.sub_params['timestamp'] = timestamp

  def run(self):
    if self.auth:
      self.auth_stamp()
    self.run = True
    loop = asyncio.get_event_loop()
    while self.run:
      try:
        loop.run_until_complete(self.connect())

      except asyncio.TimeoutError:
        logger.warn("Ping Timeout, Restarting Websocket")

      except websockets.exceptions.ConnectionClosed:
        logger.warn("Connection Closed, Restarting Websocket")

      except KeyboardInterrupt:
        logger.error("Keyboard Interuption, stopping socket")
        raise

      except Exception:
        logger.error("last message recieved "
                     f"{self.last_time_watch()} seconds ago\n"
                     f"{traceback.format_exc()}")
        logger.warn("Restarting Websocket")

  async def connect(self):
    async with websockets.connect(self.url) as self.ws:
      await self.send(json.dumps(self.sub_params))
      await self.listen()

  async def send(self, message):
    await self.ws.send(message)
    logger.info(f" > {message}")

  async def listen(self):
    listen = True
    while listen:
      try:
        recieved = await asyncio.wait_for(self.ws.recv(), timeout=50)
        if "type" in json.loads(recieved).keys():
          logger.info(f" < {json.loads(recieved)}")
        self.last_time = time.time()

      except asyncio.TimeoutError:
        await self.ping_socket()

      except websockets.exceptions.ConnectionClosed:
        listen = False
        logging.warn("Connection Closed Exception after "
                     f"{round(self.last_time_watch(), 2)} seconds")
        raise websockets.exceptions.ConnectionClosed(
          1006,
          "1 minute without messages")

      except KeyboardInterrupt:
        listen = False
        raise

      except Exception:
        listen = False
        logger.exception("Socket had a general excetption, last message "
                         f"recieved {self.last_time_watch()} seconds ago")
        raise

  async def ping_socket(self):
    logger.info("Pinging Socket")
    pong_socket = await self.ws.ping()
    await asyncio.wait_for(pong_socket, timeout=10)

  def last_time_watch(self):
    return time.time() - self.last_time

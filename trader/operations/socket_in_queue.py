import asyncio
import base64
import hashlib
import hmac
import json
import logging.config
import time

import config

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class SocketInQueue(asyncio.Queue):

  def put_message(self, action, product_id, channel):
    message = self.Message(action, product_id, channel)

    logger.debug("adding message to queue: {}".format(message))
    self._loop.call_soon_threadsafe(
      lambda: self.put_nowait(message))

  def put_stop_message(self):
    self.put_message("stop", None, None)

  async def get_message(self):
    message = await self.get()
    return message

  class Message:

    def __init__(self, action, product_id, channel, authorize=False):
      self.action = action
      self.product_id = product_id
      self.channel = channel
      self.authorize = authorize

    def __repr__(self):
      return "<{}Message: {}, {}, {}>".format(
        "Authorize " if self.authorize else "", self.action, self.product_id,
        self.channel
      )

    def get_json(self):
      return json.dumps({
        'type': self.action,
        'product_ids': [self.product_id],
        'channels': [self.channel]
      })

    def get_json_with_auth(self, api_key, api_secret, api_passphrase):
      timestamp = str(time.time())
      message = timestamp + 'GET' + '/users/self/verify'
      message = message.encode()
      hmac_key = base64.b64decode(api_secret)
      signature = hmac.new(hmac_key, message, hashlib.sha256)
      signature_b64 = base64.b64encode(signature.digest()).decode()
      return json.dumps({
        'type': self.action,
        'product_ids': [self.product_id],
        'channels': self.channel,
        'signature': signature_b64,
        'key': api_key,
        'passphrase': api_passphrase
      })

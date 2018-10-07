import asyncio
import base64
import config
import hashlib
import hmac
import json
import os
import sys
import time
import trading
import websockets
import logging

PYTHONASYNCIODEBUG = 1
logging.basicConfig(level=logging.DEBUG)


class Subscribe():
  '''Subscription Class to interact with GDAX websocket.
  '''

  def __init__(self, product_ids=[], channel=[], url="",
               subscription='subscribe', auth=False, file_path=None,
               trading_algorithm=None):

    if url == "":
      self.url = config.socket
    self.product_ids = product_ids
    self.auth = auth
    self.channel = channel
    self.subscription = subscription
    self.error = None
    self.file_path = file_path
    self.ws = websockets.connect(self.url)
    self.stop = False
    self.trading_algorithm = trading_algorithm

    if self.channel == []:
      self.sub_params = {
          'type': subscription,
          'product_ids': self.product_ids}
    else:
      self.sub_params = {
          'type': subscription,
          'product_ids': self.product_ids,
          'channels': self.channel
      }

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

  def start(self):

    if self.auth:
      self.auth_stamp()
    self.ws = self._connect()

    asyncio.get_event_loop().run_until_complete(self.ws)

  async def connect(self):
    async with websockets.connect(self.url) as ws:
      await ws.send(json.dumps(self.sub_params))
      await self._listen(ws)

  async def _listen(self, ws):
    while True:  # killing true may end loop when there is an error.
      try:
        msg = await asyncio.wait_for(ws.recv(), timeout=30)
        self.on_message(msg)

      # ping socket to keep connection alive
      except asyncio.TimeoutError:
        print("\n-- Pinging Socket --")
        try:
          pong_socket = await ws.ping()
          await asyncio.wait_for(pong_socket, timeout=30)
        # Try twice
        except asyncio.TimeoutError:
          try:
            pong_socket = await ws.ping()
            await asyncio.wait_for(pong_socket, timeout=30)
          except:
            print("\n-- No Pong --")
            break

      except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        self.on_error(e, msg)

  def on_open(self, msg):
    # Not using
    return None

#  def on_message(self, msg):
#    self.trading_algorithm.process_message(msg)

  def on_error(self, e, data=None):
    print('{}: {} , {} - data: {}'.format(type(e), e, e.args, data))
    self._disconnect()

  def _disconnect(self):
    # Need to disconnect socket when error
    print("\n-- Error => Canceling Trades --")
    '''for trade in [
        {"id": trade["id"],
         "size": trade["size"],
         "price": trade["price"],
         "side": trade["side"]
         }
        for trade
        in self.trading_algorithm.book
    ]:
    trading.cancel_id(trade)'''

  def on_close(self):
    print("\n-- Socket Closed --")

# Run as main option used for debugging websocket


if __name__ == "__main__":
  subscription = sys.argv[1]
  product_ids = sys.argv[2].split(',')
  channels = sys.argv[3].split(',')
  try:
    auth = sys.argv[4]
    try:
      main_file_path = sys.argv[5]
    except:
      main_file_path = None
  except:
    auth = False

  sock = Subscribe(
      product_ids,
      channels,
      auth=auth,
      subscription=subscription,
      file_path=main_file_path)
  sock.start()

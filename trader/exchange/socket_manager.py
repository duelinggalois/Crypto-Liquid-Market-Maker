import asyncio
import config
import base64
import hashlib
import hmac
import json
import time
import websockets


class SocketManager():

  def __init__(self,
               loop=None,
               auth=False,
               url="",
               action='subscribe',
               product_ids=[],
               channel=[]
               ):

    self.loop = asyncio.get_event_loop() if loop is None else loop
    self.thing = "thing"
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
    self.protocol = websockets.connect(self.url)

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
    self.ws = self.connect()
    self.loop.run_until_complete(self.ws)

  async def connect(self):
    async with self.protocol as ws:
      await self.send(ws, json.dumps(self.sub_params))
      await self.listen(ws)

  async def send(self, ws, message):
    await ws.send(message)
    print(f"{time.strftime('%x %X')} > {message}")

  async def listen(self, ws):
    running = True
    self.update = False
    while running:
      # if self.update:
        # ws.send(json.dumps(update_message()))
      try:
        recieved = await ws.recv()
        if "type" in json.loads(recieved).keys():
          print(f"{time.strftime('%x %X')} < {json.loads(recieved)}")
        last_time = time.time()
      except Exception:
        running = False
        print(f"{time.strftime('%x %X')} >< {time.time() - last_time}")
        raise
      finally:
        ws.close()

  def send_update(self, new_params):
    asyncio.get_event_loop().call_soon(self.update(new_params))
    print(f"> {new_params}")

  async def check_for_update(self):
    self.update = True

  def update_message(self):
    return self.updated

""">>> sock.protocol.ws_client
sock.protocol.ws_client
>>> sock.protocol.ws_client.c
sock.protocol.ws_client.client_connected(
sock.protocol.ws_client.close(
sock.protocol.ws_client.close_code
sock.protocol.ws_client.close_connection(
sock.protocol.ws_client.close_connection_task
sock.protocol.ws_client.close_reason
sock.protocol.ws_client.closed
sock.protocol.ws_client.connection_lost(
sock.protocol.ws_client.connection_lost_waiter
sock.protocol.ws_client.connection_made(
sock.protocol.ws_client.connection_open(
>>> sock.protocol.ws_client.close()
<generator object WebSocketCommonProtocol.close at 0x7f22f43451a8>
>>> sock.protocol.ws_client
sock.protocol.ws_client
>>> sock.protocol.ws_client.recv()
<generator object WebSocketCommonProtocol.recv at 0x7f22f0777728>
>>> 
"""

"""Traceback (most recent call last):
  File "/home/rev3ks/Documents/Crypto-Liquid-Market-Maker/lib/python3.6/site-packages/websockets/protocol.py", line 528, in transfer_data
    msg = yield from self.read_message()
  File "/home/rev3ks/Documents/Crypto-Liquid-Market-Maker/lib/python3.6/site-packages/websockets/protocol.py", line 580, in read_message
    frame = yield from self.read_data_frame(max_size=self.max_size)
  File "/home/rev3ks/Documents/Crypto-Liquid-Market-Maker/lib/python3.6/site-packages/websockets/protocol.py", line 645, in read_data_frame
    frame = yield from self.read_frame(max_size)
  File "/home/rev3ks/Documents/Crypto-Liquid-Market-Maker/lib/python3.6/site-packages/websockets/protocol.py", line 710, in read_frame
    extensions=self.extensions,
  File "/home/rev3ks/Documents/Crypto-Liquid-Market-Maker/lib/python3.6/site-packages/websockets/framing.py", line 100, in read
    data = yield from reader(2)
  File "/usr/lib/python3.6/asyncio/streams.py", line 672, in readexactly
    raise IncompleteReadError(incomplete, n)
asyncio.streams.IncompleteReadError: 0 bytes read on a total of 2 expected bytes

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/rev3ks/Documents/Crypto-Liquid-Market-Maker/trader/exchange/socket_manager.py", line 61, in run
    self.loop.run_until_complete(self.ws)
  File "/usr/lib/python3.6/asyncio/base_events.py", line 468, in run_until_complete
    return future.result()
  File "/home/rev3ks/Documents/Crypto-Liquid-Market-Maker/trader/exchange/socket_manager.py", line 66, in connect
    print(f"> {self.sub_params}")
  File "/home/rev3ks/Documents/Crypto-Liquid-Market-Maker/trader/exchange/socket_manager.py", line 75, in listen
    try:
  File "/home/rev3ks/Documents/Crypto-Liquid-Market-Maker/lib/python3.6/site-packages/websockets/protocol.py", line 350, in recv
    yield from self.ensure_open()
  File "/home/rev3ks/Documents/Crypto-Liquid-Market-Maker/lib/python3.6/site-packages/websockets/protocol.py", line 501, in ensure_open
    self.close_code, self.close_reason) from self.transfer_data_exc
websockets.exceptions.ConnectionClosed: WebSocket connection is closed: code = 1006 (connection closed abnormally [internal]), no reason
"""
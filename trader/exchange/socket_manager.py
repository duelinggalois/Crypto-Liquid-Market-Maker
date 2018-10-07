import config
import base64
import hashlib
import hmac
import json
import time
import websockets


class SocketManger():

  def __init__(self, loop, auth=False, url="", action='sbscribe'):
    self.loop = loop
    self.thing = "thing"
    self.auth = auth
    self.url = config.socket if url == "" else url
    if self.channel == []:
      self.sub_params = {
          'type': action,
          'product_ids': self.product_ids}
    else:
      self.sub_params = {
          'type': action,
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

  async def connect(self):
    if self.auth:
      self.auth_stamp()
    async with websockets.connect(self.url) as ws:
      connected = True
      self.protocol = ws
      await ws.send(json.dumps(self.sub_params))
      await recieved = ws.recv()
      print(f"< {recieved}")
    connected = False

  async def send_new_message(self, new_params):
    await self.ws.send(json.dumps, new_params)

  async def message(self):
    running = True
    while running:
      msg = await self.protocol.recv()
      print("> " + msg)


'''
#!/usr/bin/env python

# WS client example

import asyncio
import websockets

async def hello():
    async with websockets.connect(
            'ws://localhost:8765') as websocket:
        name = input("What's your name? ")

        await websocket.send(name)
        print(f"> {name}")

        greeting = await websocket.recv()
        print(f"< {greeting}")

asyncio.get_event_loop().run_until_complete(hello())
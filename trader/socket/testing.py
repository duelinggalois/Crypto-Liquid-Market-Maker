import asyncio
import json

import websockets

import config


async def connect(params):
  print("> " + str(params))
  async with websockets.connect(config.socket) as ws:
    await ws.send(json.dumps(params))
    print("listening")
    while True:
      rcvd = await ws.recv()
      message = json.loads(rcvd)
      print("< " + str(message))


def run(action="subscribe", product_ids=["BTC-USD"], channels=["matches"]):
  params = {"type": action, "product_ids": product_ids, "channels": channels}
  asyncio.get_event_loop().run_until_complete(connect(params))

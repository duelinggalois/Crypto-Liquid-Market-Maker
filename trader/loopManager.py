import asyncio
from .exchange.socket_manager import SocketManger


class LoopManager():

  def __init__(self):
    self.loop = asyncio.get_event_loop()
    self.url = ''

  async def main(self):
    # get trading terms
    # 
    sock = SocketManager(loop)
    sock.
    self.startLoop()

  def startLoop(self):
    self.loop.run_forever()

import config
import asyncio, websockets, time, base64, hmac, json, hashlib
import sys
import logging

file_path = "./socketdata/data.txt"
PYTHONASYNCIODEBUG = 1
logging.basicConfig(level=logging.DEBUG)


class Subscribe():
  '''Subscription Class to interact with GDAX websocket.
  '''
  
  def __init__(self, product_ids=[], channel=[], url="", 
    subscription='subscribe', auth=False, file_path=None):
    
    if url == "":
      self.url = config.socket
    self.product_ids = product_ids 
    self.auth = auth
    self.channel = channel
    self.subscription = subscription
    self.error = None
    self.ws = None
    self.file_path=file_path
    self.stop= False

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
    self.api_secret = config.api_secret
    self.api_passphrase= config.api_passphrase
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

    if auth:
      auth_stamp()
    self.ws = self._connect()

    asyncio.get_event_loop().run_until_complete(self.ws)  


  async def _connect(self):
    async with websockets.connect(self.url) as ws:
      await ws.send( json.dumps( self.sub_params ))
      await self._listen(ws)

    return ws
    
  async def _listen(self, ws):
    subsc = False
    while True:
      try:
        msg = await asyncio.wait_for(ws.recv(), timeout=20)
        while not subsc:
          # need to check for "type":"subscriptions"
          # self.on_open(msg)
          self.on_message(msg)
          subsc = True

        self.on_message(msg)
      # ping socket to keep connection alive
      except asyncio.TimeoutError:
        print("\n--pinging socket--\n")
        try:
          pong_socket = await ws.ping()
          await asyncio.wait_for(pong_socket, timeout=10)
        except:
          print("\n--no pong from socket--\n")
          break
      
      except Exception as e:
        self.on_error(e)
      

  def _disconnect(self, e):
    print(e)
    self.on_close()
  
  def close(self):
    self.stop = True
  
  def on_open(self, msg):
    print("\n-- Subscribed! --\n")
    print("{0}".format(
      msg
      )
    )
  
  def on_close(self):
    print("\n-- Socket Closed --")
  
  def on_message(self, msg):
    with open(self.file_path, 'a') as output:
      print("< {}\n".format(msg))
      output.write("< {}\n".format(msg))
  
  def on_error(self, e, data=None):
    self.error = e
    print('{} - data: {}'.format(e, data))

if __name__== "__main__":
  subscription = sys.argv[1]
  product_ids = sys.argv[2].split(',')
  channels = sys.argv[3].split(',')
  try:
    main_file_path = sys.argv[4]
    try:
      auth = sys.argv[5]
    except:
      auth = False
  except:
    main_file_path = file_path
    auth = False
  
  sock = Subscribe(
    product_ids, 
    channels, 
    auth=auth,
    subscription=subscription,
    file_path=main_file_path)
  sock.start()

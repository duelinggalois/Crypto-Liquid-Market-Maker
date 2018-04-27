import config
import asyncio, websockets, time, base64, hmac, json, hashlib
import sys

file_path = "./socketdata/data.txt"

class Subscribe():
  '''Subscription Class to interact with GDAX websocket.
  '''
  
  def __init__(self, product_ids=[], url="", channel=[], 
    subscription='subscribe', auth=False, api_key="",
    api_secret="", api_passphrase="", file_path=None):
    
    self.url = url
    self.product_ids = product_ids 
    self.auth = auth
    self.channel = channel
    self.subscription = subscription
    self.api_key = api_key
    self.api_secret = api_secret
    self.api_passphrase= api_passphrase
    self.error = None
    self.ws = None
    self.thread = None
    self.file_path=file_path
    
  def start(self):
    self._connect()
    self.on_open()  
  
  def _connect(self):     
    
    if self.channel == []:
      sub_params = {
        'type': subscription, 
        'product_ids': self.product_ids}
    else:
      sub_params = {
        'type': subscription, 
        'product_ids': self.product_ids, 
        'channels': self.channel 
      }
    
    if self.auth:
      timestamp = str(time.time())
      message = timestamp + 'GET' + '/users/self/verify'
      message = message.encode()
      hmac_key = base64.b64decode(self.api_secret)
      signature = hmac.new(hmac_key, message, hashlib.sha256)
      signature_b64 = base64.b64encode(signature.digest()).decode()
      sub_params['signature'] = signature_b64
      sub_params['key'] = self.api_key
      sub_params['passphrase'] = self.api_passphrase
      sub_params['timestamp'] = timestamp
    
    self.ws = start_to_send(
      self.url, 
      json.dumps(sub_params), 
      file_path=self.file_path)

    asyncio.get_event_loop().run_until_complete(self.ws)
  
  def _disconnect(self):
    try:
      if self.ws:
        self.ws.close()
    except WebSocketConnectionClosedException as e:
      print(e)
    self.on_close()
  
  def close(self):
    self.stop = True
    self.thread.join()
  
  def on_open(self):
    print("\n-- Subscribed! --\n")
  
  def on_close(self):
    print("\n-- Socket Closed --")
  
  def on_message(self, msg):
    print(msg)
  
  def on_error(self, e, data=None):
    self.error = e
    self.stop = True
    print('{} - data: {}'.format(e, data))

async def start_to_send(url, message_added, file_path=file_path):
  async with websockets.connect(url) as websocket:
    await websocket.send(message_added)
    with open(file_path, 'a') as output:
      print_first = True
      while True:
        info = await websocket.recv()
        if print_first:
          print("< {}\n".format(info))
          print_first = False
        output.write("< {}\n".format(info))

def run_Subscribe(product_ids, channel, subscription='subscribe', file_path=None):
  
  return Subscribe(
    product_ids, 
    url=config.socket,
    channel=channel, 
    auth=True, 
    api_key=config.api_key,
    api_secret=config.api_secret, 
    api_passphrase=config.api_pass,
    file_path=file_path)

if __name__== "__main__":
  subscription = sys.argv[1]
  product_ids = sys.argv[2].split(',')
  channels = sys.argv[3].split(',')
  try:
    main_file_path = sys.argv[4]
  except:
    main_file_path = file_path
  sock = run_Subscribe(
      product_ids, 
      channels, 
      subscription=subscription,
      file_path=main_file_path)
  sock.start()

"""
Notes on socket
>>> ETHUSD = a.run_Subscribe('ETH-USD', 'full')
>>> ETHUSD.start()
  < {"type":"subscriptions","channels":[{"name":"full","product_ids":["ETH-US
  D"]}]}
  < { 
    "type":"received",
    "order_id":"931d0197-fa5f-4521-9bfa-b96356055510",
    "order_type":"limit",
    "size":"9.00000000",
    "price":"831.03000000",
    "side":"buy",
    "client_oid":"3fff2cb2-abda-4ce9-89fd-10407093cdfe",
    "product_id":"ETH-USD",
    "sequence":2509845619,
    "time":"2018-02-11T22:55:11.673000Z"}
  < {
    "type":"open",
    "side":"buy",
    "price":"831.03000000",
    "order_id":"931d0197-fa5f-4521-9bfa-b96356055510",
    "remaining_size":"9.00000000",
    "product_id":"ETH-USD",
    "sequence":2509845620,
    "time":"2018-02-11T22:55:11.673000Z"}
"""

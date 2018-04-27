import config

class Subscribe():
  '''Subscription Class to interact with GDAX websocket.
  '''
  
  def __init__(self, pair, url="", channel=None, 
    auth=False, api_key="",api_secret="", api_passphrase=""):
    
    self.url = url
    self.pair = pair 
    self.auth = auth
    self.channel = channel
    self.api_key = api_key
    self.api_secret = api_secret
    self.api_passphrase= api_pass
    self.stop = False
    self.error = None
    self.ws = None
    self.thread = None
    
  def start(self):
    self._connect()
    self.on_open()  
  
  def _connect(self):     
    
    if self.channel is None:
      sub_params = {'type': 'subscribe', 'product_ids': self.pair}
    else:
      sub_params = {
        'type': 'subscribe', 
        'product_ids': [self.pair], 
        'channels': [self.channel] 
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
    
    self.ws = start_to_send(self.url, json.dumps(sub_params))
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
    
async def start_to_send(url, message_added):
  async with websockets.connect(url) as websocket:
    await websocket.send(message_added)
    while True:
      info = await websocket.recv()
      print("< {}".format(info))

def run_Subscribe(pair, channel):
  
  return Subscribe(
    pair, 
    url=config.socket,
    channel=channel, 
    auth=True, 
    api_key=config.api_key
    api_secret=config.api_secret 
    api_passphrase=config.api_pass)

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
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
    
  def start(self):
    self._connect()
    self.on_open() 

    asyncio.get_event_loop().run_until_complete(self.ws) 
  
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
      self.api_key = config.api_key
      self.api_secret = config.api_secret
      self.api_passphrase= config.api_passphrase
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
    
    self.ws = self.start_to_send(
      json.dumps(sub_params))
  
  async def start_to_send(self, message_added):
    async with websockets.connect(self.url) as websocket:
      await websocket.send(message_added)
      while not self.stop:
        try:
          msg = await websocket.recv()
        except websockets.exceptions.ConnectionClosed as e:
          on_error(e)
          self._disconnect(e)
        self.on_message(msg)
      

  def _disconnect(self):
    asyncio.get_event_loop().stop()
    self.on_close()
  
  def close(self):
    self.stop = True
  
  def on_open(self):
    print("\n-- Subscribed! --\n")
  
  def on_close(self):
    print("\n-- Socket Closed --")
  
  def on_message(self, msg):
    with open(self.file_path, 'a') as output:
      print("< {}\n".format(msg))
      output.write("< {}\n".format(msg))
  
  def on_error(self, e, data=None):
    self.error = e
    self.stop = True
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

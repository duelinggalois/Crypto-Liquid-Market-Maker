import json, hmac, hashlib, time, requests, base64, config
from requests.auth import AuthBase

# Create custom authentication token for GDAX Exchange
# Used https://stackoverflow.com/questions/37763235/unicode-objects-must-be-
# encoded-before-hashing-error help to get this to function with python3
class GdaxAuth(AuthBase):
  def __init__(self, api_key, secret_key, passphrase):
    self.api_key = api_key
    self.secret_key = secret_key
    self.passphrase = passphrase

  def __call__(self, request):
    timestamp = str(time.time()).encode()
    message = timestamp + request.method.encode() + request.path_url.encode() + (request.body or '')
    hmac_key = base64.b64decode(self.secret_key)
    signature = hmac.new(hmac_key, message, hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest()) 

    request.headers.update({
      'CB-ACCESS-SIGN': signature_b64,
      'CB-ACCESS-TIMESTAMP': timestamp,
      'CB-ACCESS-KEY': self.api_key,
      'CB-ACCESS-PASSPHRASE': self.passphrase,
      'Content-Type': 'application/json'
    })
    return request

# run GdaxAuth pulls keys from config and return auth
def run_GdaxAuth():
  return GdaxAuth(config.api_key, config.api_secret, config.api_pass)

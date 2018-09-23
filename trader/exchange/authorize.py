import hmac
import hashlib
import time
import requests
import base64
from requests.auth import AuthBase
import config


class GdaxAuth(AuthBase):
  def __init__(self, api_key, secret_key, passphrase):
    self.api_key = api_key
    self.secret_key = secret_key
    self.passphrase = passphrase

  def __call__(self, request):
    timestamp = str(time.time()).encode()
    message = timestamp + request.method.encode() + request.path_url.encode()
    message += (request.body or b'')
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
def run_coinbase_pro_auth():
  return GdaxAuth(config.api_key,
                  config.api_secret,
                  config.api_passphrase)


def test_run_coinbase_pro_auth():
  return GdaxAuth(config.test_api_key,
                  config.test_api_secret,
                  config.test_api_passphrase)

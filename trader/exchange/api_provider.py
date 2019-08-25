from trader.exchange.api_enum import ApiEnum
from trader.exchange.coinbase_pro import CoinbasePro, CoinbaseProTest
from trader.exchange.noop_trader import NoopApi


class ApiProvider:

  coinbase_pro = CoinbasePro()
  coinbase_pro_test = CoinbaseProTest()
  noop_api = NoopApi()

  apis = {
    ApiEnum.CoinbasePro: coinbase_pro,
    ApiEnum.CoinbaseProTest: coinbase_pro_test,
    ApiEnum.NoopApi: noop_api
  }

  @classmethod
  def get_api(cls, enum):
    return cls.apis[enum]

  @classmethod
  def get_api_keys(cls):
    return cls.apis.keys()

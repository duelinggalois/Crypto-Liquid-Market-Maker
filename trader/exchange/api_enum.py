from enum import Enum


class ApiEnum(Enum):
  """
  Enum to help categorize trading api
  """
  NoopApi = "NoopApi"
  CoinbasePro = "CoinbasePro"
  CoinbaseProTest = "CoinbaseProTest"

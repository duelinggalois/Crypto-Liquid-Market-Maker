import abc
import logging.config

from config import log_config, socket_url
from trader.exchange.api_enum import ApiEnum
from trader.database.models.trading_terms import TradingTerms
from trader.socket.manager import SocketManager
from trader.socket.reader import Reader
from trader.socket.thread_handler import ThreadHandler

logging.config.dictConfig(log_config)
logger = logging.getLogger(__name__)


class OperatorAbstract(abc.ABC):

  @abc.abstractmethod
  def start_socket(self):
    pass

  @abc.abstractmethod
  def stop_socket(self):
    pass

  @abc.abstractmethod
  def add_strategy(self, strategy):
    pass

  @abc.abstractmethod
  def remove_strategy(self, strategy):
    pass


class Operator(OperatorAbstract):

  def __init__(self, url: str = socket_url,
               api_enum = ApiEnum.CoinbasePro):
    self.api_enum = api_enum
    self.socket_manager = SocketManager(url)
    self.thread_handler = ThreadHandler(api_enum)
    self.reader = Reader(self.socket_manager.socket_out, self.thread_handler)

    self.socket_running = False

  def start_socket(self):
    self.socket_manager.start()
    self.reader.start()
    self.socket_running = True

  def stop_socket(self):
    self.socket_manager.stop()
    self.reader.join()
    self.socket_running = False

  def add_strategy(self, strategy: TradingTerms):
    if self.api_enum != self.thread_handler.trading_api.enum:
      raise ValueError(
        "strategy api, {}, does not match operators, {}.".format(
          TradingTerms.api_enum,
          self.thread_handler.trading_api.enum
        ))
    self.thread_handler.add_terms(strategy)
    self.socket_manager.add_subscription(strategy.pair)

  def remove_strategy(self, strategy: TradingTerms):
    self.socket_manager.remove_subscription(strategy.pair)
    self.thread_handler.remove_terms(strategy)

import abc
import logging.config
import threading
from queue import Queue

from config import log_config
from trader.database.db import dal

logging.config.dictConfig(log_config)
logger = logging.getLogger(__name__)


class TradingThreadBase(threading.Thread):

  def __init__(self, book_manager):

    super().__init__()

    # self.filled_order_desc = filled_order_desc
    self.book_manager = book_manager
    self.adjust_queue = Queue()
    self.started = False
    self.session_errors = 0

  def start(self):
    self.started = True
    super().start()

  def has_not_started(self):
    return not self.started

  def run(self):
    logger.debug("Running {} trading thread".format(self.__class__.__name__))
    try:
      self.book_manager.load_book()
      self.run_method()
      self.book_manager.close_book()
    except ConnectionError as e:

      self.session_errors += 1
      if self.session_errors < 3:
        logger.warning(
          "Attempting to reconnect for database exception code: {}"
          "".format(e.args)
        )
        dal.connect()
        self.run()
      else:
        raise e
    except Exception as e:
      logger.error("{} trading thread error: {}".format(
        self.__class__.__name__, e.args
      ))

  @abc.abstractmethod
  def run_method(self):
    """
    Method to be called after book is loaded and before it is closed.

    :return: None
    """
    raise NotImplementedError("This class must be implemented to use")

  def intervene(self, size, other_thread):
    """
    Intervene will signal to the thread that another thread is going to start
    and will post from the minimum size to the given size. This thread will use
    the size to determine if it should stop or pause and will start again once
    the given thread is done using the join method.
    :param size: max_size of other thread
    :param other_thread: other thread
    :return:
    """
    self.adjust_queue.put((size, other_thread))


class InitialSendOrderThread(TradingThreadBase):

  def run_method(self):
    self.book_manager.send_orders(adjust_queue=self.adjust_queue)


class AdjustOrdersThread(TradingThreadBase):

  def __init__(self, book_manager, order_description):
    self.filled_order_desc = order_description
    super().__init__(book_manager)

  def run_method(self):
    self.book_manager.send_trade_sequence(self.filled_order_desc,
                                          adjust_queue=self.adjust_queue)


class CancelOrdersThread(TradingThreadBase):

  def run_method(self):
    self.book_manager.cancel_all_orders()

import config
import logging
import logging.config
import os
from .user_interface import prompts
from .sequence.book_manager import Book_Manager
from .socket.manager import SocketManager
from .socket.reader import Reader

logging.config.dictConfig(config.log_config)
logger = logging.getLogger("trader")


def run(test=True):
  os.system('clear')
  logger.info("Running Trader")
  prompts.show_intro()

  # Get initial input from user
  terms = prompts.prompt_trading_terms(test=test)

  # Confirm user selections
  while not prompts.confirm_trading_terms(terms):
    # reprompt for input
    terms = prompts.prompt_trading_terms(test=test)

  book_manager = Book_Manager(terms, test=test)
  reader = Reader(book_manager)
  socket_manager = SocketManager(reader, product_ids=[terms.pair],
                                 send_trades=True)
  socket_manager.run()


try:
  run()
except Exception:
  logger.exception("error running trader")

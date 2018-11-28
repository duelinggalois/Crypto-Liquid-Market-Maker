import config
import logging
import logging.config
import os
from .user_interface import prompts
from .sequence.book_manager import Book_Manager

logging.config.dictConfig(config.log_config)
logger = logging.getLogger("trader")


def run():
  os.system('clear')
  logger.info("Running Trader")
  prompts.show_intro()

  # Get initial input from user
  terms = prompts.prompt_trading_terms()

  # Confirm user selections
  while not prompts.confirm_trading_terms(terms):
    # reprompt for input
    terms = prompts.prompt_trading_terms()

  book = Book_Manager(terms)


try:
  run()
except Exception:
  logger.exception("error running trader")

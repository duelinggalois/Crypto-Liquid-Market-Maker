import config
import logging
import logging.config
import os
import argparse
from decimal import Decimal

from .user_interface import prompts
from .sequence.trading_terms import TradingTerms
from .sequence.book_manager import BookManager
from .socket.manager import SocketManager
from .socket.reader import Reader

logging.config.dictConfig(config.log_config)
logger = logging.getLogger("trader")


def user_inteface(test=True):
  os.system('clear')
  logger.info("Running Trader")
  prompts.show_intro()

  # Get initial input from user
  terms = prompts.prompt_trading_terms(test=test)

  # Confirm user selections
  while not prompts.confirm_trading_terms(terms):
    # reprompt for input
    terms = prompts.prompt_trading_terms(test=test)
  return terms


def construct(terms, test):

  book_manager = BookManager(terms, test=terms.test)
  reader = Reader(book_manager)
  socket_manager = SocketManager(reader, product_ids=[terms.pair],
                                 send_trades=True)
  return socket_manager


def parse_command_line():
  parser = argparse.ArgumentParser(description='argument parser description')
  parser.add_argument('--pair', type=str, default=None)
  parser.add_argument('--budget', type=Decimal, default=None)
  parser.add_argument('--minsize', type=Decimal, default=None)
  parser.add_argument('--sizechange', type=Decimal, default=None)
  parser.add_argument('--minprice', type=Decimal, default=None)
  parser.add_argument('--test', type=bool, default=True)
  args = parser.parse_args()

  return args


def main(args):
  all_args = (args.pair and args.budget and args.minsize and
              args.sizechange and args.minprice)

  # Check for parser arguemnts to run with.
  if not all_args:
    terms = user_inteface(test=args.test)
    socket_manager = construct(terms, terms.test)
  else:
    socket_manager = construct(
      TradingTerms(
        pair=args.pair,
        budget=args.budget,
        min_size=args.minsize,
        size_change=args.sizechange,
        low_price=args.minprice,
        test=args.test),
      test=args.test)

  try:
    socket_manager.run()
  except Exception:
    logger.exception("error running trader")


# Main
args = parse_command_line()
main(args)

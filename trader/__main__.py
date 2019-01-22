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


def parse_command_line():
  parser = argparse.ArgumentParser(description='argument parser description')
  parser.add_argument('--pair', type=str, default=None)
  parser.add_argument('--budget', type=Decimal, default=None)
  parser.add_argument('--minsize', type=Decimal, default=None)
  parser.add_argument('--sizechange', type=Decimal, default=None)
  parser.add_argument('--lowprice', type=Decimal, default=None)
  parser.add_argument('--highprice', type=Decimal, default=None)
  parser.add_argument('--test', type=bool, default=True)
  args = parser.parse_args()

  return args


def main(args):
  all_args = (args.pair and args.budget and args.minsize and
              args.sizechange and (args.lowprice or
                                   args.highprice))

  # Check for parser arguemnts to run with.
  if not all_args:
    terms = user_inteface()
    socket_manager = construct(terms)
  else:
    socket_manager = construct(
      TradingTerms(
        pair=args.pair,
        budget=args.budget,
        min_size=args.minsize,
        size_change=args.sizechange,
        low_price=args.lowprice,
        high_price=args.highprice,
        test=args.test),
      test=args.test)

  try:
    socket_manager.run()
  except Exception:
    logger.exception("error running trader")


def user_inteface():
  os.system('clear')
  logger.info("Running Trader")
  prompts.show_intro()

  # Get initial input from user
  terms = prompts.prompt_trading_terms()
  return terms


def construct(terms):
  logger.debug("Construct - terms.test: {}\n{}".format(terms.test, terms))
  book_manager = BookManager(terms)
  reader = Reader(book_manager)
  socket_manager = SocketManager(reader, product_ids=[terms.pair],
                                 send_trades=True)
  return socket_manager


# Main
args = parse_command_line()
main(args)

import sys

import config
import logging
import argparse
from decimal import Decimal

from trader.user_interface.prompts import Prompts
from trader.exchange.api_wrapper.coinbase_pro import CoinbasePro
from trader.sequence.trading_terms import TradingTerms
from trader.sequence.book_manager import book_manager_maker
from trader.socket.manager import SocketManager
from trader.socket.reader import Reader

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
  parser.add_argument('--live', action='store_true')

  # QA command can be used with low price, highprice, and budget
  parser.add_argument('--qa', action='store_true')
  args = parser.parse_args()

  return args


def main(args):

  all_args = (args.pair and args.budget and args.minsize and
              args.sizechange and (args.lowprice or
                                   args.highprice))

  # Check for parser arguments to run with.
  if not all_args:
    terms = get_terms_from_interface()
    if terms is not None:
      # socket_manager = construct_trader_module(terms)
      start_with_exception_canceling(construct_trader_module(terms))
    else:
      return
  else:
    test = not args.live
    trading_api = CoinbasePro(test=test)
    socket_manager = construct_trader_module(
      TradingTerms(
        pair=args.pair,
        budget=args.budget,
        min_size=args.minsize,
        size_change=args.sizechange,
        low_price=args.lowprice,
        high_price=args.highprice,
        trading_api=trading_api
      )
    )
    start_with_exception_canceling(socket_manager)


def get_terms_from_interface():
  return Prompts().get_terms()


def construct_trader_module(terms):
  logger.debug("Trading Api using sandbox: {}".format(terms.trading_api.test))
  logger.debug("Constructing: \n{}".format(terms))
  BookManagerMaker = book_manager_maker(terms, trading_api=terms.trading_api)
  reader = Reader(BookManagerMaker)
  socket_manager = SocketManager(reader, terms.trading_api.test,
                                 product_ids=[terms.pair], send_trades=True)
  return socket_manager


def qa():
  trading_api = CoinbasePro(test=True)
  mid_price = trading_api.get_mid_market_price("BTC-USD")
  if args.lowprice and args. highprice and args.budget:
    budget = Decimal(args.budget)
    low_price = Decimal(args.lowprice)
    high_price = Decimal(args.highprice)
  elif mid_price < 500 or mid_price > 15000:
    logger.error(
      "Sandbox trading at {} outside of current qa settings, use following "
      "flags budget, highprice and lowprice".format(mid_price)
    )
    return
  else:
    budget = Decimal("50000")
    low_price = Decimal("100")
    high_price = Decimal("20000")

  terms = TradingTerms(
    pair="BTC-USD",
    budget=budget,
    min_size=Decimal(".001"),
    size_change=Decimal(".0001"),
    low_price=low_price,
    high_price=high_price,
    trading_api=trading_api
  )
  socket_manager = construct_trader_module(terms)
  start_with_exception_canceling(socket_manager)


def start_with_exception_canceling(socket_manager):
  try:
    socket_manager.run()
  except Exception as e:
    logger.error("Error running QA: {}", e)
  finally:
    for thread in socket_manager.reader.thread_handler.get_threads():
      thread.intervene(sys.maxsize, None)
      thread.join()
    logger.info("Canceling orders")
    socket_manager.reader.thread_handler.BookManagerMaker().cancel_all_orders()
    logger.info("Done")


# Main
args = parse_command_line()
if args.qa:
  qa()
else:
  main(args)

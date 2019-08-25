import sys
import time

import config
import logging
import argparse
from decimal import Decimal

from trader.exchange.api_enum import ApiEnum
from trader.exchange.api_provider import ApiProvider
from trader.operations.operator import Operator
from trader.user_interface.prompts import Prompts
from trader.exchange.coinbase_pro import (CoinbasePro,
                                          CoinbaseProTest)
from trader.database.models.trading_terms import TradingTerms

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
      operator = get_operator(terms)
      start_with_exception_canceling(operator, terms)
    else:
      return
  else:
    test = not args.live
    api_enum = ApiEnum.CoinbaseProTest if test else ApiEnum.CoinbasePro
    terms = TradingTerms(
        pair=args.pair,
        budget=args.budget,
        min_size=args.minsize,
        size_change=args.sizechange,
        low_price=args.lowprice,
        high_price=args.highprice,
        api_enum=api_enum
    )
    operator = get_operator(terms)
    start_with_exception_canceling(operator, terms)


def get_terms_from_interface():
  return Prompts().get_terms()


def get_operator(terms):
  logger.debug("Trading Api using: {}".format(terms.api_enum))
  logger.debug("Constructing Operator with terms: \n{}".format(terms))
  if terms.api_enum == ApiEnum.CoinbasePro:
    socket_url = config.socket_url
  elif terms.api_enum == ApiEnum.CoinbaseProTest:
    socket_url = config.test_socket
  else:
    raise ValueError("No socket for: {}".format(terms.api_enum))
  logger.debug("Socket url: {}".format(socket_url))
  return Operator(url=socket_url, api_enum=terms.api_enum)


def qa():
  trading_api = ApiProvider.get_api(ApiEnum.CoinbaseProTest)
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
    api_enum=trading_api.enum
  )
  operator = get_operator(terms)
  start_with_exception_canceling(operator, terms)


def start_with_exception_canceling(operator, terms):

  operator.start_socket()
  operator.add_strategy(terms)
  # run a loop to catch errors in threads or
  try:
    while operator.reader.is_alive() and operator.socket_manager.is_alive():
      time.sleep(1)
  finally:
    logger.error("Error running QA, socket is alive {}, reader is alive {}"
                 .format(operator.socket_manager.is_alive(),
                         operator.reader.is_alive()))

    logger.info("Canceling orders")
    operator.remove_strategy(terms)
    operator.stop_socket()
    logger.info("Done")


# Main
args = parse_command_line()
if args.qa:
  qa()
else:
  main(args)

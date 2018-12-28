import os
from decimal import Decimal
import readline

from pick import pick

from ..sequence.trading_terms import TradingTerms


def _input_default(prompt, default):
  def hook():
    readline.insert_text(default)
    readline.redisplay()
  readline.set_pre_input_hook(hook)
  result = input(prompt)
  readline.set_pre_input_hook()
  return result


def _prompt_decimal(title, default=""):
  while True:
    try:
      value = _input_default("\n" + title + "\n", default)
      value = Decimal(value)
    except ValueError:
      print("\nplease enter a valid value (e.g. .01, 1.75)\n")
      continue
    else:
      break
  return value


def _prompt_bool(title, default):
  while True:
    value = _input_default("\n" + title + " (y/n)\n", default)
    value = value.lower()
    if value == 'y':
      return True
    elif value == 'n':
      return False
    else:
      print("\nplease type 'y' or 'n'\n")
      continue


def _prompt_list(title, list, default_index):
  value, index = pick(list, title, default_index=default_index)
  print("\n" + title + "\n\n" + value + "\n\n")
  return value


def show_intro():
  # display header and description of program intent
  print(
    "** Crypto Liquid Market Maker - By William P. Fey **\n"
    "This program will list a sequence of buy and sell trades on \n"
    "pro.coinbase.com based on pertinent user input.\n\n"
  )
  input("Press return to continue...")
  # clear screen
  os.system('clear')


def prompt_trading_terms():

  terms = TradingTerms()

  terms.pair = _prompt_list(
    "What trading pair would you like to use?",
    terms.supported_pairs,
    0
  )

  terms.budget = _prompt_decimal(
    ("What is the value of {0} would you like to allocate in terms of {1}?"
     ).format(
      terms.base_pair,
      terms.quote_pair,
    )
  )

  terms.min_size = _prompt_decimal(
    "What is the minimum trade size for this pair?",
    terms.min_size
  )

  terms.size_change = _prompt_decimal(
    "How much should each trade in the sequence of buys and sells increase "
    "by?",
    ".000025"
  )

  print("This pair is currently trading at {0} {1}/{2}."
        .format(terms.mid_price,
                terms.base_pair,
                terms.quote_pair
                )
        )

  terms.low_price = _prompt_decimal(
    "What is the low price to buy at?"
  )

  return terms


def confirm_trading_terms(terms):
  print("here are your selections:\n")
  print(terms)
  print("\n\n")
  return _prompt_bool("would you like to proceed using these terms?", "y")


def prompt_ready_to_trade():
  if _prompt_bool("Would you like trades to be listed?", "y"):
    return True
  else:
    return _prompt_bool("Would you like to change your input?", "n")


def prompt_to_return_class():
  return _prompt_bool("Would you like to return trades as a class?", "n")

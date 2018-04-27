import trading_algorithm
import os
import readline
from pick import pick

def _input_default(prompt, default):
  def hook():
    readline.insert_text(default)
    readline.redisplay()
  readline.set_pre_input_hook(hook)
  result = input(prompt)
  readline.set_pre_input_hook()
  return result

def _prompt_float(title, default):
  while True:
    try:
      value = _input_default("\n"+title+"\n\n", default)
      value = float(value)
    except ValueError:
      print("\nplease enter a valid float value (e.g. .01, 1.75)\n\n")
      continue
    else:
      break
  return value

def _prompt_bool(title, default):
  while True:
    value = _input_default("\n"+title+"  (y/n)\n\n", default)
    value = value.lower()
    if value=='y':
      return True
    elif value=='n':
      return False
    else:
      print("\nplease type 'y' or 'n'\n\n")
      continue

def _prompt_list(title, list, default_index):
  value, index = pick(list, title, default_index=default_index)
  print("\n"+title+"\n\n"+value+"\n\n")
  return value

def show_intro():
  # display header and description of program intent
  print(
    "** Crypto Liquid Market Maker - By William P. Fey **\n"+ \
    "This program will list a sequence of buy and sell trades on \n"+ \
    "GDAX.com based on pertinent user input.\n\n"
  )
  input("Press return to continue...")
  # clear screen
  os.system('clear')

def prompt_user():
  #Prompts User for input to start algorithm, returns trading_terms.

  show_intro()

  supported_pairs = ["BTC-USD", "ETH-USD", "LTC-USD", "BCH-USD", "BTC-ETH", "LTC-BTC", "BCH-BTC"]
  pair = _prompt_list(
    "What trading pair would you like to use?",
    supported_pairs,
    6
  )
  
  budget = _prompt_float(
    ("What is the value of {0} would you like to allocate in terms of {1}?").format(pair[:3],pair[4:]),
    ".075"
  )

  min_size = _prompt_float(
    "What is the minimum trade size for this pair?",
    ".01"
  )

  size_change = _prompt_float(
    "How much should each trade in the sequence of buys and sells increase by?",
    ".000025"
  )
  
  current_price = _prompt_float(
    ("What is the estimated price of {0} in terms of {1}?").format(pair[:3], pair[4:]),
    ".15185"
  )

  use_current_price = _prompt_bool(
    ("Would you like to use {0} {1}/{2} as the the midpoint of the trading algorithm?").format(current_price, pair[4:], pair[:3]),
    "y"
  )
  
  if not use_current_price:
    mid_price = _prompt_float("What midpoint price would you like to use?")
  else:
    mid_price = current_price
  
  high_price = _prompt_float(
    "What is the highest price to be sold at?",
    ".3"
  )

  low_price = 2* mid_price - high_price

  trading_terms = trading_algorithm.TradingTerms(pair, budget, low_price, mid_price, min_size, size_change)

  return trading_terms

def prompt_ready_to_trade():
  list_trades = _prompt_bool("Would you like trades to be listed?", "n")
  if list_trades:  
    return True
  else:
    change_input = _prompt_bool("Would you like to change your input?", "n")
    return change_input

def prompt_to_return_class():
  return _prompt_bool("Would you like to return trades as a class?", "n")

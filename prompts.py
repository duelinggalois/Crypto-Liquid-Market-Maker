simport os
import readline
from pick import pick
from trading_terms import TradingTerms

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
      value = _input_default("\n"+title+"\n", default)
      value = float(value)
    except ValueError:
      print("\nplease enter a valid float value (e.g. .01, 1.75)\n")
      continue
    else:
      break
  return value

def _prompt_bool(title, default):
  while True:
    value = _input_default("\n"+title+" (y/n)\n", default)
    value = value.lower()
    if value=='y':
      return True
    elif value=='n':
      return False
    else:
      print("\nplease type 'y' or 'n'\n")
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

def prompt_trading_terms():

  terms = TradingTerms()

  terms.pair = _prompt_list(
    "What trading pair would you like to use?",
    TradingTerms.supported_pairs,
    TradingTerms.default_pair_index
  )
  
  terms.budget = _prompt_float(
    ("What is the value of {0} would you like to allocate in terms of {1}?").format(
      terms.pair_from,
      terms.pair_to
    ),
    ".075"
  )

  terms.min_size = _prompt_float(
    "What is the minimum trade size for this pair?",
    ".01"
  )

  terms.size_change = _prompt_float(
    "How much should each trade in the sequence of buys and sells increase by?",
    ".000025"
  )
  
  current_price = _prompt_float(
    ("What is the estimated price of {0} in terms of {1}?").format(
      terms.pair_from,
      terms.pair_to
    ),
    ".15185"
  )

  use_current_price = _prompt_bool(
    ("Would you like to use {0} {1}/{2} as the the midpoint of the trading algorithm?").format(
      current_price,
      terms.pair_to,
      terms.pair_from
    ),
    "y"
  )
  
  if not use_current_price:
    terms.mid_price = _prompt_float("What midpoint price would you like to use?")
  else:
    terms.mid_price = current_price
  
  terms.low_price = _prompt_float(
    "What is the low price to be sold at?",
    ".3"
  )

  return terms

def confirm_trading_terms(terms):
  print("here are your selections:\n")
  print(terms)
  print("\n\n")
  return _prompt_bool("would you like to proceed using these terms?", "y")

def prompt_ready_to_trade():
  if _prompt_bool("Would you like trades to be listed?", "n"):  
    return True
  else:
    return _prompt_bool("Would you like to change your input?", "n")

def prompt_to_return_class():
  return _prompt_bool("Would you like to return trades as a class?", "n")

import trading_algorithm
from pick import pick

def show_intro():
  # display header and description of program intent
  print(
    "** Crypto Liquid Market Maker - By William P. Fey **\n"+ \
    "This program will list a sequence of buy and sell trades on \n"+ \
    "GDAX.com based on pertinent user input.\n\n"
  )
  input("Press return to continue...")

def prompt_pair():
  # prompt user to select trading pair, validate input
  title = 'Select Trading Pair: '
  supported_pairs = ['BTC-USD', 'ETH-USD', 'LTC-USD', 'BCH-USD', 'BTC-ETH', 'LTC-BTC', 'BCH-BTC']
  selected_pair, index = pick(supported_pairs, title)
  return selected_pair

def prompt_budget(pair):
  while True:
    try:
      budget = float(input(("What is the value of {0} would you like to allocate in terms of {1}?\n\n").format(pair[:3],pair[4:])))
    except ValueError:
      print("please enter a valid float value (e.g. .075)")
      continue
    else:
      break
  return float(budget)

def prompt_user():
  #Prompts User for input to start algorithm, returns trading_terms.

  show_intro()
  ready = True
  while ready:
    try:
      pair = prompt_pair()
      budget = prompt_budget(pair)

      print("\nSize of trades")
      min_size = float(input("\nWhat is the minimum trade size for this "+\
         "pair?\n\n"))
      size_change = float(input("\nHow much should each trade in the "+ \
        "sequnce of buys and sells \nincrease by?\n\n"))
      
      print("\nPrices of trades\n")
      current_price = float(\
        input(\
        ("What is the estimated price of {0} in terms of {1}?\n\n")\
        .format(pair[:3], pair[4:])))
      use_current_price = (input(\
        ("\nWould you like to use {0} {1}/{2} as the the midpoint of "+\
         "the \ntrading algorithm? (y or n)\n\n")\
        .format(current_price, pair[4:], pair[:3])))
      if 'y' != use_current_price[:1].lower():
        mid_price = float(input("\nWhat midpoint price would you "+\
          "like to use?\n\n"))
      else: mid_price = current_price
      
      high_price = float(input(\
        "\nWhat is the highest price to be sold at?\n\n"))
      low_price = 2* mid_price - high_price
      
    # if input raises errors, ask if user would like to try again
    except:
      retry = input("Input was incorrectly formatted would you like "+\
        "to retry? (y or n)")     
      retry = retry[:1].lower()
      ready = 'y' == retry
      continue
    
    trading_terms = trading_algorithm.TradingTerms(pair, budget, low_price, mid_price, min_size, size_change)

    return trading_terms

  # if user exits input returns -1 to disrupt main from running. 
  return -1

def prompt_ready_to_trade():
  if 'y' == input("Would you like trades to be listed? (y or n)\n")[:1].lower():
    return True
  elif 'n' == input("Would you like to change input? (y or n)\n")[:1].lower():
    return False 

def prompt_to_return_class():
  if 'y' == input("Would you like to return trades as a class? (y or n)\n")[:1].lower():
    return True

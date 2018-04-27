import trading_algorithm

def prompt_user():
  '''Prompts User for input to start algorithm, returns trading_terms. 
  '''
  ready = True
  print(" ***********************Trading Algorithm************************ \
    \n ***********************By William P. Fey************************ \
    \n\n" +\
    "This program will list a squence of buy and sell trades on \n"+ \
    "GDAX.com based on the follosing input.\n")
  while ready:
    try:
      # Sizes of Trades
      print("Available Trading Pairs\n"+\
        "BTC-USD, ETH-USD, LTC-USD, BCH-USD, BTC-ETH, LTC-BTC, "+\
        "BCH-BTC\n")
      pair = input("What trading pair would you like to list?\n\n")
      budget = float(input((
        "\nWhat is the value of {0} would you like to allocate in "+\
        "terms of {1}?\n\n").format(pair[:3],pair[4:])))
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

  # if user exits inuput returns -1 to disrupt main from running. 
  return -1

def prompt_ready_to_trade():
  if 'y' == input("Would you like trades to be listed? (y or n)\n")[:1].lower():
    return True
  elif 'n' == input("Would you like to change input? (y or n)\n")[:1].lower():
    return False 

def prompt_to_return_class():
  if 'y' == input("Would you like to return trades as a class? (y or n)\n")[:1].lower():
    return True

import authorize, requests, config

def send_trade_list(
  pair, 
  side, 
  first_trade_size, 
  size_increase, 
  first_trade_price,
  price_increase, 
  trade_count,
  auth=None):

  """function takes in intial info trading pair (BTC-USD), side (buy or 
  sell), first trade price, minimum trade value, increase in price per trade,
  increase in value per trade, the number of trades and an authorization
  token and lists a corrosponding sequence of trades on GDAX through there
  API
  
  To do's : write function to accept class object instead of each item
  """
  
  auth = authorize.run_GdaxAuth()
  # Initiate trading index, trade dictionary to be sent in while-loop, and
  # neg_pos variable to help manage buy vs sell sequence direction in loop. 
  
  n = 0
  listed_trades = []
  trade = {
    "size": "",
    "price": "",
    "side": side,
    "product_id": pair
  }
  api_url = config.url

  if side == "buy":
    neg_pos = -1
  else:
    neg_pos = 1
  
  print("\n-- Listing New {}s --".format(trade["side"].title()))
  # While loop to list each trade in sequence
  while n < trade_count:
    trade["size"] = str(
      round(first_trade_size + size_increase * n, 10) 
      )
    trade["price"] = str(
      round(
        first_trade_price + neg_pos * price_increase * n, 10
        ) 
      )
    t = requests.post(api_url + 'orders', json=trade, auth=auth)
    
    #Check for error
    if t.status_code != 200:
      print(("Response: {}, Message {}, Price: {}, Size: {}").format(
        str(t.status_code),
        t.json()["message"],
        trade["price"],
        trade["size"],
        )
      )
      
    # Try to enter data into ts
    else: 
      try:
        print(("{}, Size: {}, Price: {}").format(
          t.json()["product_id"],
          t.json()["size"],
          t.json()["price"],
          )
        )
        listed_trades.append( t.json() )  
      
      except:
        print( t.json() )

    n += 1
  # Return trades 
  return listed_trades

def cancel_id(trade):
  auth = authorize.run_GdaxAuth()
  api_url = 'https://api.gdax.com/'
  response = requests.delete(api_url + 'orders/' + trade["id"], auth=auth)
  print(
    "response: {}, id: {}, side: {}, size: {}, price: {}".format(
      response.status_code,
      trade["id"],
      trade["side"],
      trade["size"],
      trade["price"]
    )
  )

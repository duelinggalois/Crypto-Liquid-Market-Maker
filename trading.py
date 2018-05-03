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
  
  print("\n--Listing {}s--".format(trade["side"]))
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

def adjust_to_trade():
  print ("adjusting to matched trade")

def adjust(pair, side, first_trade_size, size_increase, 
    first_trade_price, price_change, trade_count ):
    '''Addes cancelation of trades listed between range given to auth_and_
    list_trades funtion (if multiple strategies are in effect, this will
    cancel all orders from any strategy. 
    '''
    auth = authorize.run_GdaxAuth()
    api_url = 'https://api.gdax.com/'

    if side == 'buy':
        high = first_trade_price
        low = first_trade_price - (trade_count - 1) * price_change
    else:
        low = first_trade_price
        high = first_trade_price + (trade_count - 1) * price_change
        
    # Get list of trades for pair
    open_orders =requests.get(
        api_url + 'orders?product_id' + pair, auth=auth).json()
    
    # Cancel trades in range
    cancel(pair, side=side, high_price=high, low_price=low)

    # List new trades
    print ("\n--New Orders--")
    
    # List new trades
    trade_list = send_trade_list(
      pair, 
      side, 
      first_trade_size, 
      size_increase,
      first_trade_price, 
      price_change, 
      trade_count, 
      auth)

    return trade_list

def cancel(pair, side=None, high_price=None, low_price=None):
  auth = authorize.run_GdaxAuth()
  api_url = 'https://api.gdax.com/'

  # Get list of trades for pair
  open_orders =requests.get(
      api_url + 'orders?product_id' + pair, auth=auth).json()
  
  cancel_order_ids = [
    [ order["id"], order["price"], order["size"] ] 
    for order in open_orders
  ]

  if side:
    cancel_order_ids = [
      [ order["id"], order["price"], order["size"] ] 
      for order in cancel_order_ids if side == order["side"]
    ]
  if high_price:
    cancel_order_ids = [
      [ order["id"], order["price"], order["size"] ] 
      for order in cancel_order_ids if high_price >= order["price"]
    ]
  if low_price:
    cancel_order_ids = [
      [ order["id"], order["price"], order["size"] ] 
      for order in cancel_order_ids if low_price <= order["price"]
    ]
  
  print("\n--Canceled Orders--")
  for order_id in cancel_order_ids:
      response = requests.delete(api_url + 'orders/' + order_id[0], auth=auth)
      print(order_id[0] + ", " + order_id[1] + ", " + order_id[2])

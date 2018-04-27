import authorize, requests, config

def send_trade_list(
  pair, 
  side, 
  first_trade_size, 
  size_increase,
  price_increase, 
  first_trade_price, 
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
  ts = []
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
    
    if t.status_code != 200:
      print(("Response: {0}, Message {1}, Price: {2}, Size: {3}").format(
        str(t.status_code),
        t.json()["message"],
        trade["price"],
        trade["size"],
        )
      )

    else: 
      try:
        print(("{0}, {1}, Size: {2}, Price: {3}").format(
          t.json()["product_id"],
          t.json()["side"],
          t.json()["size"],
          t.json()["price"],
          )
        )
        ts.append( t.json() ) 
      
      except:
        print(t.json)
    n += 1

  return ts

def adjust(pair, side, first_trade_size, size_increase, 
    first_trade_price, price_change, trade_count ):
    '''Addes cancelation of trades listed between range given to auth_and_
    list_trades funtion (if multiple strategies are in effect, this will
    cancel all orders from any strategy. 
    '''
    auth = autho.run_GdaxAuth()
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
    cancel_order_ids = [
        [order["id"], order["price"], order["size"]] for order in open_orders if float(
            order["price"]) <= high and float(order["price"]) >= low]

    print('canceled orders:')
    for order_id in cancel_order_ids:
        response = requests.delete(api_url + 'orders/' + order_id[0], auth=auth)
        print(order_id[0] + ", " + order_id[1] + ", " + order_id[2])

    print ('')
    print ("New orders:")
    
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

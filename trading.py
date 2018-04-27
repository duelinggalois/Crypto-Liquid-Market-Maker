import authorize, requests

def send_trade_list(
  pair, 
  side, 
  first_trade_price, 
  first_trade_size, 
  price_increase, 
  size_increase, 
  trade_count, 
  auth):
  """function takes in intial info trading pair (BTC-USD), side (buy or 
  sell), first trade price, minimum trade value, increase in price per trade,
  increase in value per trade, the number of trades and an authorization
  token and lists a corrosponding sequence of trades on GDAX through there
  API
  
  To do's : write function to accept class object instead of each item
  """
  
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
  config = configparser.ConfigParser()
  config.read('config.ini')
  url = config['DEFAULT']
  api_url = url['url']

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

def auth_and_list_trades(
  pair, 
  side, 
  first_trade_size, 
  size_increase, 
  first_trade_price, 
  price_change, 
  trade_count ):
  '''
  creates auth token and lists sequence of trades on Exchange given a trading pair, side, first_trade_size, size_increase, first_trade_price, price_change, trade_count
  '''
  # set up authorization token and factors needed to send trades.
  auth = authorize.run_GdaxAuth()
  
  # Send trades.
  ts = send_trade_list(
    pair,
    side, 
    first_trade_price, 
    first_trade_size, 
    price_change, 
    size_increase, 
    trade_count, 
    auth)
  
  return ts
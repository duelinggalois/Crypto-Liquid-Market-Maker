import requests, math, json
import trading, subscribe, process


def start_ws_trade(self):
  self.ready_to_send = True
  self.start_ws()


def start_ws(self):
  self.socket = subscribe.Subscribe(
      [self.pair],
      ["matches"],
      trading_algorithm=self
  )
  self.socket.start()


def list_trades(self):
  """Used to send trading sequences in new_sequences to be listed
  """
  # Send each sequence in new_squences to GDAX and return orders to book
  for i in self.trading_sequences:
    self.book += trading.send_trade_list(
      self.pair, # pair
      i['side'], # side
      i['first_size'], # first_trade_size
      self.size_change*2, # size_increase
      i['first_price'], # first_trade_price
      self.price_change, #price_increase
      self.n/2 - 1 # trade_count minus 1 as trade function starts at 0
    ) 

def process_message(self, msg):
  '''used to check socket data to see if anything needs to be done.
  '''
  # Send to process which will format output for printing
  maker_order_id =  process.new(msg)

  # if sending orders logic below
  if self.ready_to_send:
    if json.loads(msg)["type"] == "subscriptions":
      print("\n-- Listing Trades -- ")
      self.list_trades()
      print("\n-- Live Matches on GDAX --")
      self.ready_to_send = False

  # Check if order matches our active trades
  if maker_order_id in [trade["id"] for trade in self.book]:
    load_msg = json.loads(msg)
    my_trade = [trade for trade in self.book if trade["id"] == maker_order_id][0]
    filled_size = float(load_msg["size"])
    remaing_in_trade = float(my_trade["size"])-float(my_trade["filled_size"])
    
    # Check to see if entire trade is filled
    if filled_size >= remaing_in_trade:
      # Remove my_trade from book
      filled_trade = self.book.pop(self.book.index(my_trade))
      # Create new sequence of trades to list in response to matched tradde
      self.adjust(filled_trade)
    
    # in the case order has been partially filled this updates
    # filled_size in order book
    else:
      # define length string formated number for for new entry
      string_length = len(my_trade["size"])
      # Pull trade from book and update filled_size and add it back
      partial_trade = self.book.pop(self.book.index(my_trade))
      partial_trade["filled_size"] = str(filled_size)[:string_length]
      self.book.append( partial_trade)

def adjust(self, filled_trade):
  ''' Logic for placing new orders when old orders are matched. 
  '''
  # Create neg_pos to point function logic plus or minus based on side
  
  if filled_trade["side"] == "buy":
    side = "sell"
    neg_pos = 1
  else: 
    side = "buy"
    neg_pos = -1
  
  # Create terms for new sequence of trades from adjusment. 
  # first_price will be the first price of new sequence of trades
  first_price = float(filled_trade["price"]) + neg_pos * self.price_change
  first_price = round(first_price, self.p_round)
  # Count is the number of new trades
  count = round( 
    (float(filled_trade["size"]) 
    - self.first_size )   
    / self.size_change + 1
  ) 
  
  # delta is the distance from upper or lower limit to first_price 
  # trades within this limit need to be canceled before new trades are listed.
  delta = math.fabs((count -.5 )* self.price_change )

  # Canceling active orders based on conditions. 
  print("\n--Trade Matched Adjusting Canceled and Relisting--")
  # For loop to pulls data from a conditional list using list comprehension. 
  for trade_info in [
    { "id": trade["id"], 
      "size": trade["size"], 
      "price": trade["price"],
      "side": trade["side"]
    } 
    for trade 
    in self.book 
    if trade["side"] == side 
    and  math.fabs(float(trade["price"]) - first_price ) < delta
  ]:
    # Cancel trade within for loop
    trading.cancel_id(trade_info)

  # Define book based on trades remaining after above cancel
  self.book = [
    trade
    for trade
    in self.book
    # Logical converse of canceled trades. 
    if not trade["side"] == side or 
    not math.fabs(float(trade["price"]) - first_price ) < delta
  ]
  # Sending new trades and add them to book 
  self.book += trading.send_trade_list(
    self.pair, # pair
    side, # side
    self.first_size, # first_trade_size
    self.size_change, # size_increase
    first_price, # first_trade_price
    self.price_change, #price_increase
    count 
  )

  # Todo: add print book function to see book as it stands after adjustments
  # self.print_book()

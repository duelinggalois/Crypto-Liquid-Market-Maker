import json

'''
This is intended to parse websocket data from subscribe and tell trading_algorithm to send 
trades when trades execute. 

maker_order_id in list of trades executes -> trading_terms.adjsut()

Where should I put the list of trades. How best should this file access that list

how best to call .adjust() once file is filled. 

Process:
Main calls prompts which creates trading_algorithm class. 

Main starts websocket 

Websocket uses process to parse data and decide if a trade has been made

trading_algroithm 
'''


file_path = "./socketdata/data.txt"

def subscription(msg):
  #Channels: {'channels': [{'product_ids': ['ETH-BTC'], 'name': 'matches'}], 'type': 'subscriptions'}   Pair: 
  load_msg = json.loads(msg)
  print("\n-- {0} --".format(load_msg["type"]))
  for c in load_msg["channels"]:
    print("Channel: {0}\t\tPair: {1}\n".format(
      c["name"],
      c["product_ids"]
      )
    )

def new (msg, file_p=None):
  file_path = "./socketdata/data.txt"
  if file_p:
    file_path = file_p
  load_msg = json.loads(msg)
  with open(file_path, 'a') as output:
    #pick_type(msg)
    print("< {0} - {1} - id: {2} - side: {3} - {4} - {5}\n{6}".format(
      load_msg["time"],
      load_msg["product_id"],
      load_msg["trade_id"],
      load_msg["side"],
      load_msg["size"],
      load_msg["price"],
      everything_else(load_msg)
      )
    )
    output.write("< {}\n".format(msg))

def everything_else(msg):
  statement = ""
  for i in msg.keys():
    if i not in [
      "time", 
      "product_id", 
      "trade_id", 
      "side", 
      "size", 
      "price", 
      "type", 
      "maker_order_id",
      "taker_order_id"]:
      statement += '"'+str(i)+'"' + '"'+str(msg[i])+'"' + ", "

  return statement[:-2] 

def pick_type(msg):
  print(msg)

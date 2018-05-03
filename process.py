import json

file_path = "./socketdata/data.txt"

def new (msg, file_p=file_path):
  '''Chooose which process function to use to process message based on message type.
  ''' 
  chooser = {
    "subscriptions": subscriptions,
    "last_match": last_match,
    "match": match,
    "error": error
  }
  func = chooser.get(json.loads(msg)["type"], other)
  func(msg, file_p)

def subscriptions(msg, file_p=file_path):
  #Channels: {'channels': [{'product_ids': ['ETH-BTC'], 'name': 'matches'}], 'type': 'subscriptions'}   Pair: 
  load_msg = json.loads(msg)
  print("\n-- Subscribed --".format(load_msg["type"]))
  for c in load_msg["channels"]:
    print("Channel: {0}\t\tPair: {1}\n".format(
      c["name"],
      c["product_ids"]
      )
    )
def last_match(msg, file_p=file_path):
  load_msg = json.loads(msg)
  print("\n-- Last Match -- ")
  print("< {0} - {1} - trade id: {2} - "
      "side: {3} size: {4} price: {5}".format(
      load_msg["time"],
      load_msg["product_id"],
      load_msg["trade_id"],
      load_msg["side"],
      load_msg["size"],
      load_msg["price"]
      )
    )

def match(msg, file_p=file_path):
  load_msg = json.loads(msg)
  print("< {0} - {1} - trade_id: {2} - "
    "side: {3} size: {4} price: {5}".format(
    load_msg["time"],
    load_msg["product_id"],
    load_msg["trade_id"],
    load_msg["side"],
    load_msg["size"],
    load_msg["price"]
    )
  )
  return load_msg["maker_order_id"]

def error(msg, file_p):
  load_msg = json.loads(msg)
  raise ProcessError(load_msg["error"])
  print("< {} message: {}".format(
    load_msg["error"],
    load_msg[""]
    )
  )

def other(msg, file_p):
  load_msg = json.loads(msg)
  statement = "< "
  for i in load_msg.keys():
    statement += '"'+ i +'"' + '"'+ str(load_msg[i]) +'"' + ", "
  print( statement[:-2] )

def save_to_file(msg, file_p=file_path):
  with open(file_p, 'a') as output:
    #pick_type(msg)
    output.write("< {}\n".format(msg))
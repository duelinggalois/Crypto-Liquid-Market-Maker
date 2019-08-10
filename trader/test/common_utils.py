def create_match(order):
  return {
    "type": "match",
    "trade_id": 10,
    "sequence": 50,
    "maker_order_id": order.exchange_id,
    "taker_order_id": "132fb6ae-456b-4654-b4e0-d681ac05cea1",
    "time": "2014-11-07T08:19:27.028459Z",
    "product_id": "BTC-USD",
    "size": order.size,
    "price": order.price,
    "side": "buy"
  }


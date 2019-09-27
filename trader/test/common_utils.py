def create_match(order):
  return create_match_details(order.exchange_id, order.size, order.price)


def create_match_details(
  exchange_id, size, price, type="match", trade_id=10, operations=50,
):
  return {
    "type": type,
    "trade_id": trade_id,
    "operations": operations,
    "maker_order_id": exchange_id,
    "taker_order_id": "132fb6ae-456b-4654-b4e0-d681ac05cea1",
    "time": "2014-11-07T08:19:27.028459Z",
    "product_id": "BTC-USD",
    "size": size,
    "price": price,
    "side": "buy"
  }


def create_last_match():
  return {
    'type': 'last_match',
    'trade_id': 73794261,
    'maker_order_id': '38a653c6-04e7-4a4b-91e1-93fbcba2126a',
    'taker_order_id': 'a88ca9cd-6714-4d19-be34-a543d2910a81',
    'side': 'sell',
    'size': '0.00114081',
    'price': '10295.84000000',
    'product_id': 'BTC-USD',
    'sequence': 10809683115,
    'time': '2019-09-10T03:19:38.190000Z'
  }


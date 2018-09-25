from ..exchange.book import Book


class Book_Manager():

  def __init__(self, terms, test=False):

    self.terms = terms
    self.book = Book(terms.pair, test)

    count = terms.trade_count
    buy_count = int(
      (terms.mid_price - terms.low_price) /
      (terms.high_price - terms.low_price) * count
    )
    sell_count = int(
      (terms.high_price - terms.mid_price) / 
      (terms.high_price - terms.low_price) * count
    )
    first_buy_size = terms.min_size
    first_sell_size = terms.min_size + terms.size_change
    first_buy_price = terms.mid_price - terms.price_change
    first_sell_price = terms.mid_price + terms.price_change
    print("Count {} buys {} sells {}".format(count, buy_count, sell_count))
    self.add_orders("buy", buy_count, first_buy_size, first_buy_price)
    self.add_orders("sell", sell_count, first_sell_size, first_sell_price)

  def add_orders(self, side, count, first_size, first_price):
    price = first_price
    size = first_size
    plus_or_minus = -1 if side == "buy" else 1
    for i in range(count):
      self.book.add_order(side, size, price)
      print("Adding a {} {} order size {} and price {}". format(
        side, self.terms.pair, size, price))

      new_size = size + self.terms.size_change * 2
      size = round(new_size, 8)
      new_price = price + plus_or_minus * self.terms.price_change
      price = round(new_price, self.terms.price_decimals)

  def send_orders(self):
    self.book.send_orders()

  def add_and_send_orders(self, side, count, first_size, first_price):
    existing_unsent_orders = self.book.unsent_ordrs
    self.book.unsent_oders = []
    self.add_orders(side, count, first_size, first_price)
    self.send_orders()
    self.book.unsent_orders = existing_unsent_orders

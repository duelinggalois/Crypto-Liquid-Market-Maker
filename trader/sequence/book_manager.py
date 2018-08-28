from ..exchange.book import Book


class Book_Manager():

  def __init__(self, terms, test=False):

    self.terms = terms
    self.book = Book(terms.pair, test)

    half_count = int(terms.trade_count / 2)
    first_buy_size = terms.min_size + terms.size_change
    first_sell_size = terms.min_size
    first_buy_price = terms.mid_price - terms.price_change
    first_sell_price = terms.mid_price + terms.price_change

    self.add_orders("buy", half_count, first_buy_size, first_buy_price)
    self.add_orders("sell", half_count, first_sell_size, first_sell_price)

  def add_orders(self, side, count, first_size, first_price):
    price = first_price
    size = first_size
    plus_or_minus = -1 if side == "buy" else 1
    for i in range(count):
      self.book.add_order(side, size, price)

      size += self.terms.size_change * 2
      price += plus_or_minus * self.terms.price_change

  def send_orders(self):
    self.book.send_orders()

  def add_and_send_orders(self, side, count, first_size, first_price):
    existing_unsent_orders = self.book.unsent_ordrs
    self.book.unsent_oders = []
    self.add_orders(side, count, first_size, first_price)
    self.send_orders()
    self.book.unsent_orders = existing_unsent_orders


from ..exchange.book import Book
import config
import logging
import logging.config


logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class Book_Manager():

  def __init__(self, terms, test=False):

    self.terms = terms
    self.book = Book(terms.pair, test)

    self.initial_count = terms.trade_count
    self.buy_count = int(
      (terms.mid_price - terms.low_price) /
      (terms.high_price - terms.low_price) * self.initial_count
    )
    logger.info("rounded buy count to {}".format(self.buy_count))
    self.sell_count = int(
      (terms.high_price - terms.mid_price) /
      (terms.high_price - terms.low_price) * self.initial_count
    )
    logger.info("rounded sell count to {}".format(self.sell_count))
    self.count = self.buy_count + self.sell_count
    first_buy_size = terms.min_size
    first_sell_size = terms.min_size + terms.size_change
    first_buy_price = terms.mid_price - terms.price_change
    first_sell_price = terms.mid_price + terms.price_change
    logger.info("Count {} buys {} sells {}".format(self.initial_count,
                                                   self.buy_count,
                                                   self.sell_count))
    self.add_orders("buy",
                    self.buy_count,
                    first_buy_size,
                    first_buy_price,
                    self.terms.size_change * 2)
    self.add_orders("sell",
                    self.sell_count,
                    first_sell_size,
                    first_sell_price,
                    self.terms.size_change * 2)

  def add_orders(self, side, count, first_size, first_price, size_change):
    price = first_price
    size = first_size
    plus_or_minus = -1 if side == "buy" else 1
    for i in range(count):
      self.book.add_order(side, size, price)
      logger.info("Adding a {} {} order size {} and price {}". format(
        side, self.terms.pair, size, price))

      new_size = size + size_change
      size = round(new_size, 8)
      new_price = price + plus_or_minus * self.terms.price_change
      price = round(new_price, self.terms.price_decimals)

  def send_orders(self):
    self.book.send_orders()

  def add_and_send_orders(self, side, count, first_size, first_price, size_change):
    existing_unsent_orders = self.book.unsent_orders
    self.book.unsent_orders = []
    self.add_orders(side, count, first_size, first_price, size_change)
    self.send_orders()
    self.book.unsent_orders = existing_unsent_orders

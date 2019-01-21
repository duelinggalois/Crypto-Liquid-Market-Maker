from decimal import Decimal
import logging
import logging.config

from ..exchange.book import Book
import config

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class BookManager():

  def __init__(self, terms, test=False):
    self.terms = terms
    self.test = test
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
      logger.debug("Adding a {} {} order size {} and price {}". format(
        side, self.terms.pair, size, price))

      new_size = size + size_change
      size = round(new_size, 8)
      new_price = price + plus_or_minus * self.terms.price_change
      price = round(new_price, self.terms.price_decimals)

  def send_orders(self):
    self.book.send_orders()

  def check_match(self, match):
    if self.matched_book_order(match):
      logger.info("****MATCHED TRADE*****")
      order = next(
        o for o in self.book.open_orders if o.id == match["maker_order_id"]
      )

      if self.full_match(match, order):
        logger.info("****FOUND FULL*****")
        side, plus_minus = ("buy", -1) if order.side == "sell" else ("sell", 1)
        count = int(1 +
                    (order.size - self.terms.min_size) /
                    self.terms.size_change)
        first_size = self.terms.min_size
        first_price = order.price + plus_minus * self.terms.price_change
        self.cancel_orders_below_size(side, order.size)
        self.add_and_send_orders(side, count, first_size, first_price,
                                 self.terms.size_change)

      else:
        logger.info("****NOT FULL*****")
        order.filled += Decimal(match["size"])

  def matched_book_order(self, match):
    return match["maker_order_id"] in {
      order.id for order in self.book.open_orders
    }

  def full_match(self, match, order):
    logger.info("****CHECK FULL*****")
    return Decimal(match['size']) == order.size - order.filled

  def add_and_send_orders(self, side, count, first_size, first_price,
                          size_change):
    logger.info("****SENDING ORDERS FOR ADJUSTMENT*****")
    existing_unsent_orders = self.book.unsent_orders
    self.book.unsent_orders = []
    self.add_orders(side, count, first_size, first_price, size_change)
    self.send_orders()
    self.book.unsent_orders = existing_unsent_orders

  def cancel_orders_below_size(self, side, size):
    logger.info("****CANCELING ORDERS FOR ADJUSTMNET*****")
    orders_to_cancel = [o for o in self.book.open_orders
                        if o.side == side and o.size <= size]
    self.book.cancel_order_list(orders_to_cancel)

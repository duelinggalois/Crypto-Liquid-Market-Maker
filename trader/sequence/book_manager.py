from decimal import Decimal
import logging
import logging.config

from ..exchange.book import Book
import config
from ..database.manager import session, test_session

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class BookManager():

  def __init__(self, terms, persist=True):
    self.terms = terms
    self.test = terms.test
    self.persist = persist
    logger.debug("BookManager.test: {}".format(self.test))
    self.book = Book(terms.pair, persist=persist, test=self.test)

    first_buy_price = terms.mid_price - terms.price_change
    first_sell_price = terms.mid_price + terms.price_change
    first_buy_size = terms.min_size + terms.size_change * terms.skew

    if terms.skew < 0:
      raise NotImplemented("More buys then sells, not implemented yet")

    elif terms.skew > 0:
      # Add skewed orders and reset initial sell price and sell size
      first_sell_size = terms.min_size
      self.add_orders('sell',
                      terms.skew,
                      first_sell_size,
                      first_sell_price,
                      terms.size_change
                      )
      # Reset intials for rmeainder of trades
      first_sell_price += terms.price_change * terms.skew
      first_sell_size += terms.size_change * (terms.skew + 1)
    else:
      first_sell_size = terms.min_size + terms.size_change

    self.add_orders("buy",
                    terms.buy_count,
                    first_buy_size,
                    first_buy_price,
                    terms.size_change * 2
                    )
    self.add_orders("sell",
                    terms.sell_count - terms.skew,
                    first_sell_size,
                    first_sell_price,
                    terms.size_change * 2
                    )

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
    if self.persist:
      logger.debug(
        ("Committing {} {}s to database with status of 'ready' to be sent to "
         "exchange")
        .format(
          count, side)
      )
      if self.test:
        test_session.commit()
      else:
        session.commit()

  def send_orders(self):
    self.book.send_orders()
    if self.persist:
      if self.test:
        test_session.commit()
      else:
        session.commit()

  def check_match(self, match):
    if self.matched_book_order(match):
      logger.info("*MATCHED TRADE*")
      order = next(
          o for o in self.book.open_orders
          if o.exchange_id == match["maker_order_id"]
      )

      if self.full_match(match, order):

        # Mark order as filled
        self.book.order_filled(order.id)

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
        matched = Decimal(match["size"])
        logger.info("Partialy filled, {} filled {}."
                    .format(matched, order.size - order.filled))
        order.filled += matched
        if self.persist:
          order.save()
          order.session.commit()

  def matched_book_order(self, match):
    if logger.isEnabledFor(logging.DEBUG):
      logger.debug("Checking matched maker_order_id: {}".format(
        match["maker_order_id"]
      ))
      logger.debug("Found: {}".format(match["maker_order_id"] in {
        order.exchange_id for order in self.book.open_orders
      }))
    return match["maker_order_id"] in {
        order.exchange_id for order in self.book.open_orders
    }

  def full_match(self, match, order):
    logger.info("*CHECK FULL*")
    return Decimal(match['size']) == order.size - order.filled

  def add_and_send_orders(self, side, count, first_size, first_price,
                          size_change):
    logger.info("*SENDING ORDERS FOR ADJUSTMENT*")
    existing_unsent_orders = self.book.unsent_orders
    self.book.unsent_orders = []
    self.add_orders(side, count, first_size, first_price, size_change)
    self.send_orders()
    self.book.unsent_orders = existing_unsent_orders

  def cancel_orders_below_size(self, side, size):
    logger.info("*CANCELING ORDERS FOR ADJUSTMNET*")
    orders_to_cancel = [o for o in self.book.open_orders
                        if o.side == side and o.size <= size]
    self.book.cancel_order_list(orders_to_cancel)
    if self.persist:
      if self.test:
        test_session.commit()
      else:
        session.commit()

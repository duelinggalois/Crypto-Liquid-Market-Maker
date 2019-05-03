from decimal import Decimal
import logging
import logging.config

from deprecated import deprecated

from ..exchange.book import Book
import config
from ..database.manager import session, test_session
from trader.database.manager import (
  BaseWrapper, Engine, Test_Engine)

logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class BookManager():

  def __init__(self, terms, persist=True):
    self.terms = terms
    self.test = terms.test
    self.persist = persist
    logger.debug("BookManager.test: {}".format(self.test))

    # Temporary home for table creation
    if terms.test:
      BaseWrapper.metadata.create_all(Test_Engine)
    else:
      BaseWrapper.metadata.create_all(Engine)

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
      # Reset initials for remainder of trades
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
        self.when_full_match(order)
      else:
        self.when_partial_match(Decimal(match["size"]), order)

  def when_full_match(self, order):
    # Mark order as filled
    self.book.order_filled(order)

    side, plus_minus = ("buy", -1) if order.side == "sell" else ("sell", 1)
    count = int(1 +
                (order.size - self.terms.min_size) /
                self.terms.size_change)
    first_price = order.price + plus_minus * self.terms.price_change
    self.adjust_orders_for_matched_trade(
      side, count, first_price)

  def when_partial_match(self, filled_size, order):
    logger.info("Partially filled, {} was filled, {} remaining."
                .format(filled_size, order.size - order.filled))
    order.filled += filled_size
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

  def adjust_orders_for_matched_trade(
    self, side, count, price):
    """
    When an open order is matched, the matched value is distributed across the
    opposite side trades by adjusting all of those smaller then the matched
    trade by the size change. To do this, each trade must be canceled and
    reposted at the adjusted amount.
    """
    logger.info("*ADJUSTING ORDERS FOR MATCHED TRADE*")
    # list first trade right away
    size = self.terms.min_size
    self.add_and_send_order(side, size, price)
    plus_or_minus = -1 if side == "buy" else 1
    for i in range(count - 1):
      self.book.cancel_order_by_attribute(side, size)
      price = price + (plus_or_minus * self.terms.price_change)
      size = size + self.terms.size_change
      self.add_and_send_order(side, size, price)

  def add_and_send_order(self, side, size, price):
    self.book.add_and_send_order(side, size, price)

from trading_order import TradingOrder

class TradingSequence():

  def __init__(self, terms, side):

    self.terms = terms
    self.orders = []

    make_orders(side)


    TradingOrder(
      "sell",
      terms.min_size,
      terms.mid_price + terms.price_change,
      int(terms.max_trades/2)
    )

    first_buy_order = Trading_Order(
      "buy",
      terms.min_size + terms.size_change,
      terms.mid_price - terms.price_change,
      int(terms.max_trades/2)
    )

    self._orders.append(first_sell_order)
    self._orders.append(first_buy_order)

    return

    # add definition of orders property here
  @property
  def orders(self):
    return self._orders

  # add definition of terms property here
  @property
  def terms(self):
    return self._terms

  @terms.setter
  def terms(self, value):
    self._terms = value


  def __str__(self):

    strings = {'buy' : [], 'sell' : []}
    budgets = {'buy' : 0 , 'sell' : 0}

    # Header
    output = 'buys'+'\t'*5+'sells\n'

    # Build strings "size BOT @ price TOP / BOT" where pair = TOP-BOT
    for order in self.orders:
      # for loop through trade counts = i['n']
      for j in range(0, order.num_trades-1):

        size = round( order.size * self.terms.size_change * 2 , 5)
        price = round( order.price + order.pos_neg * j * self.terms.price_change, 5)

        strings[order.side].append(
          "{0} {1} @ {2} {3}/{1}".format(
            order.size,
            self.terms.pair_from,
            order.price,
            self.terms.pair_to
          )
        )

        if order.side == 'buy':
          budgets['buy'] += order.size * order.price
        else:
          budgets['sell'] += order.size

    # Print strings expect out of range error if sizes are unequal
    for i in range(0, len(strings['buy'])):
      output += strings['buy'][i] + '\t' * 2 + strings['sell'][i] + '\n'

    output += ('Buy budget: {0} {1}, Sell budget {2} {3} roughly worth {4} {1} '+
      'based on {5} {1}/{3} midmarket price.').format(
        round(budgets['buy'], self.terms.p_round),
        self.terms.pair_to,
        round(budgets['sell'], self.terms.p_round),
        self.terms.pair_from,
        round(budgets['sell'] * self.terms.mid_price, self.terms.p_round),
        self.terms.mid_price
      )

    return output


import requests, math, json
import trading, subscribe, process

class Trading_Sequence():

def print_trades(self):
  '''Print list of trades to be reveiwed
  '''
     
  strings = {'buy' : [], 'sell' : []}
  budgets = {'buy' : 0 , 'sell' : 0}
  
  # Header
  print ( '\n' )
  print( 'buys'+'\t'*5+'sells' )   
  
  # Build strings "size BOT @ price TOP / BOT" where pair = TOP-BOT
  for i in self.trading_sequences:
    # for loop through trade counts = i['n']
    for j in range(0, int(i['n']-1)):
      
      # -1 or 1 depending on i['side']
      pos_neg = 1 - 2 * ('buy' == i['side'])
  
      size = round ( i['first_size'] + j * self.size_change * 2 , 5)
      price = round (
        i['first_price'] + pos_neg * j * self.price_change, 5)
      
      strings[i['side']].append(
        "{0} {1} @ {2} {3}/{1}".format(
          size, self.pair[:3], price, self.pair[4:] 
          )
        )
      
      if i['side'] == 'buy':
        budgets['buy'] += size * price
      else:
        budgets['sell'] += size
    
  # Print strings expect out of range error if sizes are unequal
  for i in range(0, len(strings['buy'])):
    print( strings['buy'][i] + '\t' * 2 + strings['sell'][i] )
  
  print ( '\n' )
  print ( ('Buy budget: {0} {1}, Sell budget {2} {3} roughly worth {4} {1} '+
    'based on {5} {1}/{3} midmarket price.').format(
      round(budgets['buy'], self.p_round),
      self.pair[4:],
      round(budgets['sell'], self.p_round),
      self.pair[:3], 
      round(budgets['sell'] * self.mid_price, self.p_round),
      self.mid_price
    ) 
  )

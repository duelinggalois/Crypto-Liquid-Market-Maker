## Crypto Liquid Market Maker

I created this strategy in an attempt to automate small gains repeatedly. A set amount is intended to be allocated to the stategry and as pairs of buys and sells execute over time, profit is generated. As a price is dropping, this strategy will repeatedly buy more crypto, as prices rise, it sells more. If the range of price breaks out of the trading range that is set, no more trades will execute unless the price returns to the range. This is not financial advice and this program can result in losses. Use at your own risk.

This program will list a sequence of buy and sell trades on GDAX.com based on the following parameters:  
* trading pair (BTC-USD, ETH-USD, LTC-USD, BCH-USD, BTC-ETH, LTC-BTC, BCH-BTC)
* budget
* minimum trade size
* trade increase increment
* estimated trade price
* midpoint (optional)
* highest sale price

**Recommended Installation**
* [Install Python3](http://docs.python-guide.org/en/latest/starting/install3)
* [Install PipEnv](https://docs.pipenv.org/)
* `git clone https://github.com/rev3ks/Crypto-Liquid-Market-Maker`
* `cd Crypto-Liquid-Market-Maker`
* `cp config.ini.default config.ini`
* Add GDAX API passphrase, keys, and secret to config.ini
* `pipenv install` (dependencies managed by `Pipfile` in project root)
* `pipenv run python -m main`

**Example of Using Main**

See below if you would like python shell instructions to import modules.

`What trading pair would you like to list?` **ETH-BTC**  
`What is the value of BCH would you like to allocate in terms of BTC?` **0.8**  
`What is the minimum trade size for this pair?` **.01**  
`How much should each trade in the sequnce of buys and sells increase by?` **.0005**  
`What is the estimated price of ETH in terms of BTC?` **.0786**  
`Would you like to use 0.1125 BTC/BCH as the the midpoint of the trading algorithm? (y or n)` **y**
`What is the highest price to be sold at?` **.12835**  

**Printed Trades for Review**
```
buys					sells
0.0105 ETH @ 0.07805 BTC/ETH		0.01 ETH @ 0.07915 BTC/ETH
0.0115 ETH @ 0.0775 BTC/ETH		0.011 ETH @ 0.0797 BTC/ETH
0.0125 ETH @ 0.07695 BTC/ETH		0.012 ETH @ 0.08025 BTC/ETH
0.0135 ETH @ 0.0764 BTC/ETH		0.013 ETH @ 0.0808 BTC/ETH
0.0145 ETH @ 0.07585 BTC/ETH		0.014 ETH @ 0.08135 BTC/ETH
0.0155 ETH @ 0.0753 BTC/ETH		0.015 ETH @ 0.0819 BTC/ETH
0.0165 ETH @ 0.07475 BTC/ETH		0.016 ETH @ 0.08245 BTC/ETH
0.0175 ETH @ 0.0742 BTC/ETH		0.017 ETH @ 0.083 BTC/ETH
0.0185 ETH @ 0.07365 BTC/ETH		0.018 ETH @ 0.08355 BTC/ETH
0.0195 ETH @ 0.0731 BTC/ETH		0.019 ETH @ 0.0841 BTC/ETH
...									...

...									...
0.0905 ETH @ 0.03405 BTC/ETH		0.09 ETH @ 0.12315 BTC/ETH
0.0915 ETH @ 0.0335 BTC/ETH		0.091 ETH @ 0.1237 BTC/ETH
0.0925 ETH @ 0.03295 BTC/ETH		0.092 ETH @ 0.12425 BTC/ETH
0.0935 ETH @ 0.0324 BTC/ETH		0.093 ETH @ 0.1248 BTC/ETH
0.0945 ETH @ 0.03185 BTC/ETH		0.094 ETH @ 0.12535 BTC/ETH
0.0955 ETH @ 0.0313 BTC/ETH		0.095 ETH @ 0.1259 BTC/ETH
0.0965 ETH @ 0.03075 BTC/ETH		0.096 ETH @ 0.12645 BTC/ETH
0.0975 ETH @ 0.0302 BTC/ETH		0.097 ETH @ 0.127 BTC/ETH
0.0985 ETH @ 0.02965 BTC/ETH		0.098 ETH @ 0.12755 BTC/ETH
0.0995 ETH @ 0.0291 BTC/ETH		0.099 ETH @ 0.1281 BTC/ETH

Buy budget: 0.23179 BTC, Sell budget 4.905 ETH roughly worth 0.38553 BTC based on 
0.0786 BTC/ETH midmarket price.

Would you like trades to be listed? (y or n)
y
```

**Output**
```
-- Last Match -- 
< 2018-05-03T04:41:43.620000Z - ETH-BTC - trade id: 4699790 - side: sell size: 1.52318962 price: 0.07863000

-- Subscribed --
Channel: matches		Pair: ['ETH-BTC']


--Listing Trades-- 

--Listing sells--
ETH-BTC, Size: 0.01000000, Price: 0.07915000
ETH-BTC, Size: 0.01100000, Price: 0.07970000
ETH-BTC, Size: 0.01200000, Price: 0.08025000
...

--Listing buys--
ETH-BTC, Size: 0.01050000, Price: 0.07805000
ETH-BTC, Size: 0.01150000, Price: 0.07750000
ETH-BTC, Size: 0.01250000, Price: 0.07695000

--Live Matches on GDAX--
< 2018-05-03T04:41:44.459000Z - ETH-BTC - trade_id: 4699791 - side: sell size: 0.96902862 price: 0.07863000
< 2018-05-03T04:41:44.459000Z - ETH-BTC - trade_id: 4699792 - side: sell size: 6.30321200 price: 0.07863000
< 2018-05-03T04:41:44.459000Z - ETH-BTC - trade_id: 4699793 - side: sell size: 6.30320576 price: 0.07863000
< 2018-05-03T04:41:44.459000Z - ETH-BTC - trade_id: 4699794 - side: sell size: 0.01000000 price: 0.07863000
...
```
When Trades Execute
```
...

...
```
Socket ping socket everyonce in a while when trading is low.
```
...
< 2018-05-03T09:22:59.966000Z - ETH-BTC - trade_id: 4702810 - side: sell size: 0.10586000 price: 0.07764000

-- Pinging Socket --

-- Pinging Socket --
< 2018-05-03T09:24:19.343000Z - ETH-BTC - trade_id: 4702811 - side: sell size: 0.00000822 price: 0.07764000
< 2018-05-03T09:24:19.343000Z - ETH-BTC - trade_id: 4702812 - side: sell size: 0.01083642 price: 0.07764000
```

**Alternative use from a python shell**

```
>>> from trading_algorithm import TradingTerms 
>>> ETH_BTC = TradingTerms(pair, budget, low_price, mid_price, min_size, size_change)
>>> ETH_BTC.print_trades()
```
See *Printed Trades for Reveiw* for `print_trades()` output.
```
>>> ETH_BTC.start_ws_trade()
```
See *Output* for `start_ws_trade()` output.

**Manual Adjustments**

As trades execute, the proceeds are relisted for at a margin. For example after three trades were sold in a single price movement in the `ETH-BTC` pair, the `trading.adjust()` function relists those trades:

```
#python3.6
>>> trading.adjust('ETH-USD', 'buy', .01, .0025, 655.56, 18.68, 5)
canceled orders:
0b902cd7-5309-4663-832a-8f6db3136885, 580.84000000, 0.01250000
258bde0d-21be-4714-9488-033fbfae9527, 599.52000000, 0.01000000

New orders:
ETH-USD, buy, Size: 0.01000000, Price: 655.56000000
ETH-USD, buy, Size: 0.01250000, Price: 636.88000000
ETH-USD, buy, Size: 0.01500000, Price: 618.20000000
ETH-USD, buy, Size: 0.01750000, Price: 599.52000000
ETH-USD, buy, Size: 0.02000000, Price: 580.84000000
```

This will be automated once the websocket is completed. 

**Work In Progress**

Trading manually on GDAX for two years was a great inspiration to learn python. I still have a lot to learn and this is an outline of what I am currently working on:

* storing trading data into a database for analysis and computing tax basis and procedes automatically. 
* Cleaning up my code to be better organized and easier to understand.
* implementing unit testing.
* Implementing new ideas into strategy like using percentage change rather than a fixed change in price or fluxuating frequency rather than increasing each sequential trades value to achive the same goal. 

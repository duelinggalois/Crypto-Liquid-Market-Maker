## Crypto Liquid Market Maker

I created this strategy in an attempt to automate small gains repeatedly. A set amount is intended to be allocated to the strategy and as pairs of buys and sells execute over time, profit is generated. As a price is dropping, this strategy will repeatedly buy more crypto, as prices rise, it sells more. If the range of price breaks out of the trading range that is set, no more trades will execute unless the price returns to the range. This is not financial advice and this program can result in losses. Use at your own risk.

This program will list a sequence of buy and sell trades on pro.coinbase.com based on the following parameters:
* trading pair (BTC-USD, ETH-USD, LTC-USD, BCH-USD, BTC-ETH, LTC-BTC, etc)
* budget
* minimum trade size
* trade increase increment
* low sale price (high price currently set automatically)

**Requirements**
* [Install Python3](http://docs.python-guide.org/en/latest/starting/install3)
* [Install PipEnv](https://docs.pipenv.org/)
* [Install MySQL](https://dev.mysql.com/downloads/installer/)
* [Coinbase Pro Account](https://pro.coinbase.com)
* [Coinbase API Keys](https://pro.coinbase.com/profile/api)
* [Coinbase Test API Keys](https://public.sandbox.pro.coinbase.com/profile/api) if you want to run tests

**Recommended Installation**
* `git clone https://github.com/rev3ks/Crypto-Liquid-Market-Maker`
* `cd Crypto-Liquid-Market-Maker`
* `cp config.py.default config.py`
* Add Coinbase Pro API passphrase, keys, and secret to `config.py`
* Add MySQL credentials and name of databases to use to `config.py`
* `sudo pipenv install` (dependencies managed by `Pipfile` in project root)
* `pipenv run python -m trader` (Skip the config and run this to get a glimps)

**Alternatively run from the command line**
```
$ pipenv shell
$ python -m trader --pair ETH-USD --budget 10000 --minsize .01 --sizechange .001 --lowprice 20 [--highpirce 1000 --live] 
```
without the `--live` flag trades witll be listed on the coinbase pro test exchange, with it, trades will be sent to the live exchange.

**Running Tests**
Please note that one test will create a limit buy order at a fraction of the current market rate of BTC-USD and then cancel it. When the market rate is $10,000/BTC the order would be 0.01 BTC at a rate of $100 and would require a balance of $1 All other tests execute in the Coinbase Sandbox for fake crypto and fake money. If you do not want this test to send a trade, don't add your keys and the test will then fail when trying to send the order to coinbase.
* Add Coinbase Pro Sandbox API passphrase, keys, and secret to `config.py`
* `pipenv run nosetests --with-coverage --cover-package=trader`

**Example of Using Main**

See below if you would like python shell instructions to import modules.

```
What trading pair would you like to use?

   BAT-USDC
   BCH-BTC
   BCH-EUR
   BCH-GBP
   BCH-USD
   BTC-EUR
   BTC-GBP
 * BTC-USD
   BTC-USDC
   CVC-USDC
   DAI-USDC
   DNT-USDC
   ETC-BTC
   ETC-EUR
   ...
   ZRX-BTC
   ZRX-EUR
   ZRX-USD

```
`What is the value of BTC would you like to allocate in terms of USD?` *10000*

`What is the minimum trade size for this pair?` 
*.01*

`How much should each trade in the sequence of buys and sells increase by?` 
*.001*

```
2019-01-01 12:31:22,240 [INFO] trader.sequence.trading_terms: BTC-USD currently trading at 7876.09
This pair is currently trading at 7876.09 BTC/USD.

What is the low price to buy at?
```
*1000*

```
2019-01-01 12:32:28,836 [INFO] trader.sequence.trading_terms: With mid price of 7876.09 low price was set to 1000.00
2019-01-01 12:32:28,836 [INFO] trader.sequence.trading_terms: No high price so it was set to 14752.18
here are your selections:

2019-01-01 12:32:28,836 [INFO] trader.sequence.trading_terms: Calculating trade count with budget of 10000
2019-01-01 12:32:28,836 [INFO] trader.sequence.trading_terms: Count set to 50
base currency: 			BTC
quote currency: 		USD
budget: 			10000
min size: 			0.01
size change: 			0.00100000
low price: 			1000.00
mid price: 			7876.09
high price: 			14752.18
trade_count: 			50
price change: 			275.04




would you like to proceed using these terms? (y/n)

```

**Printed Trades for Review**
```
base currency: 			BTC
quote currency: 		USD
budget: 			10000
min size: 			0.01
size change: 			0.00100000
low price: 			3000.00
mid price: 			7876.09
high price: 			12752.18
trade_count: 			47
price change: 			207.49

would you like to proceed using these terms? (y/n)

y
```

**Output**
```
would you like to proceed using these terms? (y/n)
y
2019-01-01 12:34:27,075 [INFO] trader.sequence.BookManager: rounded buy count to 25
2019-01-01 12:34:27,075 [INFO] trader.sequence.BookManager: rounded sell count to 25
2019-01-01 12:34:27,075 [INFO] trader.sequence.BookManager: Count 50 buys 25 sells 25
2019-01-01 12:34:27,346 [INFO] trader.socket.manager: > {"type": "subscribe", "product_ids": ["BTC-USD"], "channels": ["matches"]}
2019-01-01 12:34:27,406 [INFO] trader.socket.reader: Last Match
2019-01-01 12:34:27,406 [INFO] trader.socket.reader: < 2019-01-01T19:10:02.884000Z - BTC-USD - trade id: 2194571 - side: buy size: 0.01000000 price: 8370.00000000
2019-01-01 12:34:27,728 [INFO] trader.exchange.trading: Order Posted: BTC-USD buy 0.01000000 7601.05000000
2019-01-01 12:34:28,124 [INFO] trader.exchange.trading: Order Posted: BTC-USD buy 0.01200000 7326.01000000
2019-01-01 12:34:28,289 [INFO] trader.exchange.trading: Order Posted: BTC-USD buy 0.01400000 7050.97000000
...
2019-01-01 12:34:33,302 [INFO] trader.exchange.trading: Order Posted: BTC-USD buy 0.05800000 1000.09000000
2019-01-01 12:34:33,612 [INFO] trader.exchange.trading: Order Posted: BTC-USD sell 0.01100000 8151.13000000
2019-01-01 12:34:33,913 [INFO] trader.exchange.trading: Order Posted: BTC-USD sell 0.01300000 8426.17000000
2019-01-01 12:34:34,088 [INFO] trader.exchange.trading: Order Posted: BTC-USD sell 0.01500000 8701.21000000
...
2019-01-01 12:34:38,783 [INFO] trader.exchange.trading: Order Posted: BTC-USD sell 0.05900000 14752.09000000
2019-01-01 12:34:38,783 [INFO] trader.socket.reader: Subscribed
2019-01-01 12:34:38,783 [INFO] trader.socket.reader: Channel: matches		Pair: ['BTC-USD']
2019-01-01 12:35:28,786 [INFO] trader.socket.manager: > ping
2019-01-01 12:36:18,798 [INFO] trader.socket.manager: > ping
2019-01-01 12:36:55,684 [INFO] trader.socket.reader: < 2019-01-01T19:37:05.362000Z - BTC-USD - trade_id: 2194572 - side: sell size: 0.37537611 price: 7968.08000000
2019-01-01 12:37:07,886 [INFO] trader.socket.reader: < 2019-01-01T19:37:17.557000Z - BTC-USD - trade_id: 2194573 - side: sell size: 0.05934353 price: 7968.08000000
2019-01-01 12:37:07,887 [INFO] trader.socket.reader: < 2019-01-01T19:37:17.558000Z - BTC-USD - trade_id: 2194574 - side: sell size: 0.01100000 price: 8151.13000000

```
When Trades Execute
```
2019-01-01 12:37:12,855 [INFO] trader.socket.reader: < 2019-01-01T19:37:17.558000Z - BTC-USD - trade_id: 2194577 - side: sell size: 0.01700000 price: 8976.25000000
2019-01-01 12:37:12,855 [INFO] trader.sequence.BookManager: *MATCHED TRADE*
2019-01-01 12:37:12,856 [INFO] trader.sequence.BookManager: *CHECK FULL*
2019-01-01 12:37:12,857 [INFO] trader.sequence.BookManager: *FOUND FULL*
2019-01-01 12:37:12,857 [INFO] trader.sequence.BookManager: *CANCELING ORDERS FOR ADJUSTMNET*
2019-01-01 12:37:13,015 [INFO] trader.exchange.trading: Order Deleted with id:['0b7a03de-85bd-400f-80d9-2e243e612a0c']
2019-01-01 12:37:13,147 [INFO] trader.exchange.trading: Order Deleted with id:['18909e30-ead8-4cec-a5cb-d015fb51b5ee']
2019-01-01 12:37:13,283 [INFO] trader.exchange.trading: Order Deleted with id:['0a4e46f8-b453-413f-8b1e-e0d67210df2f']
2019-01-01 12:37:13,616 [INFO] trader.exchange.trading: Order Deleted with id:['72bbf34c-0f31-45b5-9e2b-9d9de44aa681']
2019-01-01 12:37:13,743 [INFO] trader.exchange.trading: Order Deleted with id:['c2652e7a-29fe-47b8-8c36-ed13e6aa9c05']
2019-01-01 12:37:13,881 [INFO] trader.exchange.trading: Order Deleted with id:['1f63afd0-8f5e-4b82-8d31-8fb74c25590a']
2019-01-01 12:37:14,026 [INFO] trader.exchange.trading: Order Deleted with id:['95adcf93-f209-431f-b0f2-50c90a2a2093']
2019-01-01 12:37:14,026 [INFO] trader.sequence.BookManager: *SENDING ORDERS FOR ADJUSTMENT*
2019-01-01 12:37:14,321 [INFO] trader.exchange.trading: Order Posted: BTC-USD buy 0.01000000 8701.21000000
2019-01-01 12:37:14,470 [INFO] trader.exchange.trading: Order Posted: BTC-USD buy 0.01100000 8426.17000000
2019-01-01 12:37:14,886 [INFO] trader.exchange.trading: Order Posted: BTC-USD buy 0.01200000 8151.13000000
2019-01-01 12:37:15,206 [INFO] trader.exchange.trading: Order Posted: BTC-USD buy 0.01300000 7876.09000000
2019-01-01 12:37:15,355 [INFO] trader.exchange.trading: Order Posted: BTC-USD buy 0.01400000 7601.05000000
2019-01-01 12:37:15,779 [INFO] trader.exchange.trading: Order Posted: BTC-USD buy 0.01500000 7326.01000000
2019-01-01 12:37:16,078 [INFO] trader.exchange.trading: Order Posted: BTC-USD buy 0.01600000 7050.97000000
2019-01-01 12:37:16,231 [INFO] trader.exchange.trading: Order Posted: BTC-USD buy 0.01700000 6775.93000000
2019-01-01 12:37:16,232 [INFO] trader.socket.reader: < ***** 2019-01-01T19:37:17.558000Z - BTC-USD - trade_id: 2194578 - side: sell size: 0.22620620 price: 9000.00000000
```

**Work In Progress**

Trading manually on coinbase for two years was a great inspiration to learn python. I still have a lot to learn and this is an outline of what I am currently working on:

* Adding test where missing
* Adding database
* Storing trading data into a database for analysis and computing tax basis and proceeds automatically.
* Improving interface options for initialization. 

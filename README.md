## Crypto Liquid Market Maker

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
* `cd liquidcrypy`
* `pipenv install` (dependencies managed by `Pipfile` in project root)
* `pipenv run python -m main`

**Example of Using Main**

`What trading pair would you like to list?` **BCH-BTC**  
`What is the value of BCH would you like to allocate in terms of BTC?` **.05**  
`What is the minimum trade size for this pair?` **.01**  
`How much should each trade in the sequnce of buys and sells increase by?` **.000025**  
`What is the estimated price of BCH in terms of BTC?` **.15251**  
`Would you like to use 0.1125 BTC/BCH as the the midpoint of the trading algorithm? (y or n)` **y**  
`What is the highest price to be sold at?` **.3**  

**Output**
```
buys					sells
0.01025 BCH @ 0.14022 BTC/BCH		0.01 BCH @ 0.1648 BTC/BCH
0.01075 BCH @ 0.12793 BTC/BCH		0.0105 BCH @ 0.17709 BTC/BCH
0.01125 BCH @ 0.11564 BTC/BCH		0.011 BCH @ 0.18938 BTC/BCH
0.01175 BCH @ 0.10335 BTC/BCH		0.0115 BCH @ 0.20167 BTC/BCH
0.01225 BCH @ 0.09106 BTC/BCH		0.012 BCH @ 0.21396 BTC/BCH
0.01275 BCH @ 0.07877 BTC/BCH		0.0125 BCH @ 0.22625 BTC/BCH
0.01325 BCH @ 0.06648 BTC/BCH		0.013 BCH @ 0.23854 BTC/BCH
0.01375 BCH @ 0.05419 BTC/BCH		0.0135 BCH @ 0.25083 BTC/BCH
0.01425 BCH @ 0.0419 BTC/BCH		0.014 BCH @ 0.26312 BTC/BCH
0.01475 BCH @ 0.02961 BTC/BCH		0.0145 BCH @ 0.27541 BTC/BCH
0.01525 BCH @ 0.01732 BTC/BCH		0.015 BCH @ 0.2877 BTC/BCH


Buy budget: 0.024866009999999997 BTC, Sell budget 0.28600000000000003 BCH roughly worth 0.032175 BTC based on 0.1125 BTC/BCH midmarket price.
Would you like trades to be listed? (y or n)
y

Listing Trades

BCH-BTC, buy, 0.01025000, 0.14022000, <Response [200]>
BCH-BTC, buy, 0.01075000, 0.12793000, <Response [200]>
BCH-BTC, buy, 0.01125000, 0.11564000, <Response [200]>
BCH-BTC, buy, 0.01175000, 0.10335000, <Response [200]>
BCH-BTC, buy, 0.01225000, 0.09106000, <Response [200]>
BCH-BTC, buy, 0.01275000, 0.07877000, <Response [200]>
BCH-BTC, buy, 0.01325000, 0.06648000, <Response [200]>
BCH-BTC, buy, 0.01375000, 0.05419000, <Response [200]>
BCH-BTC, buy, 0.01425000, 0.04190000, <Response [200]>
BCH-BTC, buy, 0.01475000, 0.02961000, <Response [200]>
BCH-BTC, buy, 0.01525000, 0.01732000, <Response [200]>
BCH-BTC, buy, 0.01575000, 0.00503000, <Response [200]>

```

**Work In Progress**

Trading manually on GDAX for two years was a great inspiration to learn python. I still have a lot to learn and this is an outline of what I am currently working on:

* Parsing data from GDAX websocket to trigger new trades when listed trades execute. 
* storing trading data into a database for analysis and computing tax basis and procedes automatically. 
* Implementing new ideas into strategy like using percentage change rather than a fixed change in price or fluxuating frequency rather than increasing each sequential trades value to achive the same goal. 
* Cleaning up my code to be better organized and easier to understand.

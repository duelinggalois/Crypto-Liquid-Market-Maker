import trading_algorithm as ta

# Start main program
def run_main():
    '''
    will@will-VirtualBox:~/Documents/GDAX-HFT/liquidcrypy$ python3 -m main
    ***********************Trading Algorithm************************         
    ***********************By William P. Fey************************         
    
    This program will list a squence of buy and sell trades on 
    GDAX.com based on the follosing input.
    
    Available Trading Pairs
    BTC-USD, ETH-USD, LTC-USD, BCH-USD, BTC-ETH, LTC-BTC, BCH-BTC
    
    What trading pair would you like to list?
    
    BCH-BTC
    
    What is the value of BCH would you like to allocate in terms of BTC?
    
    .075
    
    Size of trades
    
    What is the minimum trade size for this pair?
    
    .01
    
    How much should each trade in the sequnce of buys and sells 
    increase by?
    
    .001
    
    Prices of trades
    
    What is the estimated price of BCH in terms of BTC?
    
    ..1125
    Input was incorrectly formatted would you like to retry? (y or n)y
    Available Trading Pairs
    BTC-USD, ETH-USD, LTC-USD, BCH-USD, BTC-ETH, LTC-BTC, BCH-BTC
    
    What trading pair would you like to list?
    
    BCH-BTC
    
    What is the value of BCH would you like to allocate in terms of BTC?
    
    .075
    
    Size of trades
    
    What is the minimum trade size for this pair?
    
    .01
    
    How much should each trade in the sequnce of buys and sells 
    increase by?
    
    .001
    
    Prices of trades
    
    What is the estimated price of BCH in terms of BTC?
    
    .1125
    
    Would you like to use 0.1125 BTC/BCH as the the midpoint of the 
    trading algorithm? (y or n)
    
    y
    
    What is the highest price to be sold at?
    
    .1625
    
    
    buys					sells
    0.011 BCH @ 0.10893 BTC/BCH		0.01 BCH @ 0.11607 BTC/BCH
    0.013 BCH @ 0.10536 BTC/BCH		0.012 BCH @ 0.11964 BTC/BCH
    0.015 BCH @ 0.10179 BTC/BCH		0.014 BCH @ 0.12321 BTC/BCH
    0.017 BCH @ 0.09822 BTC/BCH		0.016 BCH @ 0.12678 BTC/BCH
    0.019 BCH @ 0.09465 BTC/BCH		0.018 BCH @ 0.13035 BTC/BCH
    0.021 BCH @ 0.09108 BTC/BCH		0.02 BCH @ 0.13392 BTC/BCH
    0.023 BCH @ 0.08751 BTC/BCH		0.022 BCH @ 0.13749 BTC/BCH
    0.025 BCH @ 0.08394 BTC/BCH		0.024 BCH @ 0.14106 BTC/BCH
    0.027 BCH @ 0.08037 BTC/BCH		0.026 BCH @ 0.14463 BTC/BCH
    0.029 BCH @ 0.0768 BTC/BCH		0.028 BCH @ 0.1482 BTC/BCH
    0.031 BCH @ 0.07323 BTC/BCH		0.03 BCH @ 0.15177 BTC/BCH
    0.033 BCH @ 0.06966 BTC/BCH		0.032 BCH @ 0.15534 BTC/BCH
    0.035 BCH @ 0.06609 BTC/BCH		0.034 BCH @ 0.15891 BTC/BCH
    
    
    Buy budget: 0.024866009999999997 BTC, Sell budget 0.28600000000000003 BCH roughly worth 0.032175 BTC based on 0.1125 BTC/BCH midmarket price.
    Would you like trades to be listed? (y or n)
    y
    Listing trades, user CTRL+c to kill
    
    Trades would be listed when next line is uncommented

    '''
    run = True
    while run:  
        # Get initial input for starting trading aglogrithm
        trade_terms = ta.prompt_user()
        
        # Print preview of trades
        trade_terms.print_trades()
        
        # Ask user if he would like to allow trades to be made.
        ready_to_list_trades = ta.prompt_ready_to_trade()
        
        if ready_to_list_trades:
            print("Listing trades, user CTRL+c to kill\n")
            
            #############
            # List trades here
            print('Trades would be listed when next line is uncommented')
            
            # trade_terms.list_trades()
            
            ##############
             
            run = False
        elif prompt_to_return_class():
            return trade_terms
        
        elif ready_to_list_trades == None:
            # Start while loop over
            continue
            
        else:
            # End while loop
            print("Thank you for using!")
            run = False


if __name__ == '__main__':
    run_main()
    

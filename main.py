import os
import prompts

# Start main program
def run_main():
  #Main flow of program

  # clear screen
  os.system('clear')

  prompts.show_intro()
  
  # Get initial input from user
  terms = prompts.prompt_trading_terms()

  # Confirm user selections
  while not prompts.confirm_trading_terms(terms):
    # reprompt for input
    terms = prompts.prompt_trading_terms()
  
    # # Print preview of trades
    # terms.print_trades()
    
    # # Ask user if he would like to allow trades to be made.
    # ready_to_list_trades = prompts.prompt_ready_to_trade()
    
    # if ready_to_list_trades:
    #   print("Listing trades, use (CTRL + c) to kill\n")
      
    #   # List trades here
    #   trade_terms.start_ws()
    #   trade_terms.list_trades()
             
    #   run = False
    # elif prompts.prompt_to_return_class():
    #   return trade_terms
    
    # elif ready_to_list_trades == None:
    #   # Start while loop over
    #   continue
      
    # else:

  print("Thank you for playing!")


if __name__ == '__main__':
  run_main()

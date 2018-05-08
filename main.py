import os
import prompts
from trading_sequence import Trading_Sequence

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
  
  sequence = Trading_Sequence(terms)

  print(sequence.orders)

  # Print preview of trades
  print(sequence.toString());
    
  # # Ask user if he would like to allow trades to be made.
  # if prompts.prompt_ready_to_trade():
  #   print("Listing trades, use (CTRL + c) to kill\n")
      
  #   # List trades here
  #   terms.start_ws_trade()
  #   terms.list_trades()
      
  # elif prompts.prompt_to_return_class():
  #   return terms

  print("Thank you for playing!")

if __name__ == '__main__':
  run_main()

import trading_algorithm as ta
import prompts

# Start main program
def run_main():
  '''Main flow of program
  '''
  
  run = True
  while run:  
    # Get initial input for starting trading aglogrithm
    trade_terms = prompts.prompt_user()
    if trade_terms == -1:
      break

    # Print preview of trades
    trade_terms.print_trades()
    
    # Ask user if he would like to allow trades to be made.
    ready_to_list_trades = prompts.prompt_ready_to_trade()
    
    if ready_to_list_trades:
      print("Listing trades, user CTRL+c to kill\n")
      
      # List trades here
      
      trade_terms.list_trades()
             
      run = False
    elif prompts.prompt_to_return_class():
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
  

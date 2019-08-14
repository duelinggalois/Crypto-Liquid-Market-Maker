import os
from decimal import Decimal, InvalidOperation
import readline

from pick import pick

from trader.exchange.api_wrapper.coinbase_pro import CoinbasePro
from trader.sequence.trading_terms import TradingTerms

NAVIGATE = ["Back", "Menu", "Exit"]
HEADER = lambda terms: "Current Terms:\n{}\n\n".format(str(terms))


class Prompts:

  def __init__(self):
    self.state = 0
    self.ready = False
    self.exit = False
    self.terms = TradingTerms()
    self.keep_min = True
    self.use_high = True
    self.states = {
      0: ("Menu", self._menu),
      1: ("Set Api to test or live", self._prompt_test),
      2: ("Set trading pair", self._prompts_pair),
      3: ("Set budget", self._prompt_budget),
      4: ("Use default minimum allowed size", self._prompt_change_min),
      5: ("Set minimum trade size", self._prompt_min_size),
      6: ("Set size change", self._prompt_size_change),
      7: ("Set low price", self._prompt_low_price),
      8: ("Use default high price", self._prompt_use_high_price),
      9: ("Set high price", self._prompt_high_price),
      10: ("Ready to trade", self._prompts_ready_to_trade),
      -1: ("Exit", self._exit)
    }

  def get_terms(self):
    self.state = 0
    self._prompt_terms()
    if self.exit:
      return
    return self.terms

  def _get_name(self, state):
    return self.states[state][0]

  def _get_prompt(self, state):
    return self.states[state][1]

  def _prompt_terms(self):
    self._show_intro()
    while not self.ready:
      prompt = self._get_prompt(self.state)
      prompt()

  @staticmethod
  def _show_intro():
    # display header and description of program intent
    os.system('cls' if os.name == 'nt' else 'clear')
    print(
      "** Crypto Liquid Market Maker **\n"
      "This program will list a sequence of buy and sell trades on \n"
      "pro.coinbase.com based on pertinent user input.\n\n"
    )
    input("Press return to continue...")
    # clear screen
    os.system('cls' if os.name == 'nt' else 'clear')

  def _menu(self):
    value = self._prompt_list("Menu:",
                              [self._get_name(state) for state
                               in self.states if state not in {-1, 0}],
                              menu=True
                              )
    if value is not None:
      self.state = next(s for s in self.states if self._get_name(s) == value)

  def _prompt_test(self):
    test = self._prompt_bool(
      "When testing, trades will be sent to public.sandbox.pro.coinbase.com\n"
      "Are you testing?",
      0
    )
    if test is not None:
      self.terms.trading_api = CoinbasePro(test=test)
      self.state += 1

  def _prompts_pair(self):
    pair = self._prompt_list(
      "What trading pair would you like to use?",
      self.terms.supported_pairs,
      0
    )
    if pair is not None:
      self.terms.pair = pair
      self.terms.set_mid_price()
      self.state += 1

  def _prompt_budget(self):
    budget = self._prompt_decimal(
      ("What is the value of {} would you like to allocate in terms of {}?"
       ).format(self.terms.base_pair, self.terms.quote_pair)
    )
    if budget is not None:
      self.terms.budget = budget
      self.state += 1

  def _prompt_change_min(self):
    keep_min = self._prompt_bool(
      "The minimum trade size is {} would you like to keep this as the minimum "
      "trade size for the strategy? Increasing the minimum trade size will "
      "decrease the number of trades.".format(self.terms.base_min_size),
      0
    )
    if keep_min is not None:
      self.state += 1
      self.keep_min = keep_min
      if self.terms.min_size != self.terms.base_min_size:
        self.terms.min_size = self.terms.base_min_size

  def _prompt_min_size(self):
    if self.keep_min:
      self.state += 1
      return
    question = (
      "The minimum size for {} is {} What is the minimum trade size you would "
      "like to use?").format(
          self.terms.pair, self.terms.base_min_size
    )
    while True:
      min_size = self._prompt_decimal(question, str(self.terms.min_size))
      if min_size is not None:
        try:
          self.terms.min_size = min_size
        except ValueError as e:
          if str(e.args) not in question:
            question += "\nError:" + str(e.args[0])
          continue
        self.state += 1
        return
      else:
        return

  def _prompt_size_change(self):
    size_change = self._prompt_decimal(
      "How much should each trade in the sequence of buys and sells increase "
      "by?",
      str(self.terms.min_size / 50)
    )
    if size_change is not None:
      self.terms.size_change = size_change
      self.state += 1

  def _prompt_low_price(self):
    question = (
      "This pair is currently trading at {} {}/{}.\n\nWhat is the low price to "
      "be at?"
    ).format(
      self.terms.mid_price, self.terms.base_pair, self.terms.quote_pair
    )
    while True:
      low_price = self._prompt_decimal(
        question
      )
      if low_price is not None:
        try:
          self.terms.low_price = low_price
        except ValueError as e:
          if str(e.args) not in question:
            question += "\nError:" + str(e.args[0])
          continue
        self.state += 1
        return
      else:
        return

  def _prompt_use_high_price(self):
    use_high = self._prompt_bool(
      "High price is set to {}.\n\nWould you like to keep this as the high "
      "price?"
      .format(self.terms.high_price),
      0
    )
    if use_high is not None:
      self.use_high = use_high
      self.state += 1

  def _prompt_high_price(self):
    if self.use_high:
      self.state += 1
      return
    question = "What would you like the high price to be at?"
    while True:
      high_price = self._prompt_decimal(
        question,
        str(self.terms.high_price)
      )
      if high_price is not None:
        try:
          self.terms.high_price = high_price
        except ValueError as e:
          if str(e.args) not in question:
            question += "\nError:" + str(e.args[0])
          continue
        self.state += 1
        return
      else:
        return

  def _prompts_ready_to_trade(self):
    ready_to_trade = self._prompt_bool(
      "Would you like to continue with these terms?",
      1
    )
    if ready_to_trade is not None:
      if ready_to_trade:
        self.ready = True
      else:
        self.state = 0
    else:
      if self.state == 9 and self.use_high:
        # need to set state back twice to avoid returning here
        # when back is selected
        self.state -=1

  def _exit(self):
    self.ready = True
    self.exit = True

  def _prompt_bool(self, title, default=0):

    options = ["Yes", "No"] + NAVIGATE
    title = HEADER(self.terms) + title
    value, index = pick(options, title,
                        default_index=default)
    print("\n" + title + "\n" + value + "\n")
    if value == 'Yes':
      return True
    elif value == 'No':
      return False
    elif value == "Back":
      self.state -= 1
    elif value == "Menu":
      self.state = 0
    else:
      self.state = -1

  def _prompt_list(self, title, options, default_index=0, menu=False):
    os.system('cls' if os.name == 'nt' else 'clear')
    if menu:
      all_options = options + NAVIGATE[-1:]
    else:
      all_options = options + NAVIGATE
    title = HEADER(self.terms) + title
    value, index = pick(all_options, title, default_index=default_index)
    os.system('cls' if os.name == 'nt' else 'clear')
    if value in options:
      return value
    else:
      if value.lower() in ("back", "b"):
        self.state -= 1
      elif value.lower() in ("menu", "m"):
        self.state = 0
      else:
        self.state = -1

  def _prompt_decimal(self, title, default=""):
    title = HEADER(self.terms) + title

    while True:
      try:
        value = self._input_default(title + "\n", default)
        if value.lower() in ("back", "b"):
          self.state -= 1
          return
        if value.lower() in ["menu", "m"]:
          self.state = 0
          return
        if value.lower() in ["exit", "e"]:
          self.state = -1
          return
        value = Decimal(value)
        return value
      except InvalidOperation:
        if "please enter a valid value" in title:
          continue
        title += "please enter a valid value (e.g. .01, 1.2)\n"
        continue
      finally:
        os.system('cls' if os.name == 'nt' else 'clear')

  @staticmethod
  def _input_default(prompt, default):

    def hook():
      readline.insert_text(default)
      readline.redisplay()

    readline.set_pre_input_hook(hook)
    result = input(prompt + "\nEnter Menu, Back, or Exit to navigation\n\n")
    readline.set_pre_input_hook()
    os.system('cls' if os.name == 'nt' else 'clear')

    return result

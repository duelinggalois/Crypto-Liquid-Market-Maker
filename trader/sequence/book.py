

class Builder():

  def __init__(self, terms, side):

    self.terms = terms
    self.order = []

    self.make_orders()

  def make_orders(self):

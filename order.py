import trading, time

class Order():

    def __init__(pair, side, size, price):
        self.pair = pair
        self.side = side
        self.size = size
        self.price = price
        
        self.status = "Init"
        self.id = ""
        self.history = [{"init_at": time.time()}]

    def place_order(self):
        trading.send_order(self)

    def cancel_placed_order(self):
        trading.cancel_order(self)


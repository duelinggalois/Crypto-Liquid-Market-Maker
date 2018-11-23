import unittest
import mock
from ..exchange.socket_manager import SocketManager


class TestSocketManager(unittest.TestCase):

  def test_start_socket(self):
    sock = SocketManager(product_ids=["LTC-USD"], channel=["matches"])
    sock.run()

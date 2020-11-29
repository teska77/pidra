from unittest import TestCase
from network import oscclient


class TestOSCClient(TestCase):
    def test_start(self):
        client = oscclient.OSCClient()
        client.start()
from unittest import TestCase
from pidra.network.libnetwork import *
import socket


class TestSocketServer(TestCase):
    def test_run(self):
        sockserver = SocketServer()
        sockserver.run(self.handle_message)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 65435))
        for i in range(0, 1):
            sock.send(("a" * 2048 + "f").encode())
        sock.close()

    def handle_message(self, message):
        print(message)


class TestSocketThread(TestCase):
    def test_run(self):
        self.fail()


class TestMessage(TestCase):
    def test_encode(self):
        message = Message("Hello World!")
        print(message.encode())
        messenger = Messenger(None)
        messenger.recv_buffer = message.encode()
        messenger.process()


class TestSocketClient(TestCase):
    def test_send(self):
        self.fail()

    def test_run(self):
        self.client = SocketClient(('192.168.1.17', 25575), self.message_handler)
        self.client.send(encode('Hello!'))
        self.client.run()

    def test_process_message(self):
        self.fail()

    def message_handler(self, message):
        print(message)

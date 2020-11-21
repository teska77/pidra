import socket
import struct
import json
import selectors
import time
import types
"""
    Networking library - William Campany
    #multi-connection-server
    Contains some code and concepts from https://realpython.com/python-sockets/

"""

def log(*string, log=False):
    return_string = ''
    for single_string in list(string):
        return_string += str(single_string) + ' '
    return_string = return_string[:len(return_string)-1]
    if log:
        print(return_string)

def decode(message):
    header_byte_len = 2
    header_length = struct.unpack(">H", message[:header_byte_len])[0]
    body = message[header_byte_len:]
    header = json.loads(body[:header_length].decode("UTF-8"))
    content = body[header_length:header["content-length"] +
        header_length].decode(header["content-encoding"])
    return content # [:len(content - 2)]


def get_header(message):
    header_byte_len = 2
    header_length = struct.unpack(">H", message[:header_byte_len])[0]
    body = message[header_byte_len:]
    header = json.loads(body[:header_length].decode("UTF-8"))
    return (header_byte_len, header_length, header)


def encode(contents, type="text", encoding="UTF-8"):
    dict = {"content-type": type,
            "content-encoding": encoding,
            "content-length": len(contents)}
    heading_string = json.dumps(dict)
    heading_byte_len = struct.pack(">H", len(heading_string))
    heading_bytes = heading_string.encode("UTF-8")
    contents_bytes = contents.encode(encoding)
    return_bytes = bytes(heading_byte_len + heading_bytes + contents_bytes)
    # if len(return_bytes) < 1024:
    #     return_bytes += (b'\0' * (1024 - len(return_bytes)))
    return return_bytes

def realtime_encode(message, encoding="UTF-8"):
    send_bytes = message.encode(encoding)
    if len(send_bytes) < 1024:
        send_bytes += (b'\0' * (1024 - len(send_bytes)))
    return send_bytes


class LightSocketClient:
    def __init__(self, address, message_handler):
        self.client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = address
        self.message_handler = message_handler
        self.connect()

    def connect(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.address)

    def send(self, message):
        try:
            self.client.sendall(message)
            self.receive()
        except (socket.timeout, ConnectionError, ConnectionRefusedError, ConnectionResetError):
            print("Lost connection! Attempting to reconnect")
            self.connect()

    def receive(self):
        if self.client:
            buffer = self.client.recv(1024)
            self.message_handler(decode(buffer))


class SocketClient:
    def __init__(self, address, message_handler):
        self.client: socket.socket = None
        self.address = address
        self.stop = False
        self.message_handler = message_handler
        self.send_buffer = bytes()
        self.receive_buffer = bytes()
        self.remaining_content = 0
        self.header_length = 0
        self.is_running = False

    def send(self, data):
        self.send_buffer += data

    def connect(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(1)
        self.client.connect(self.address)
        self.client.setblocking(False)

    def run(self):
        while not self.stop:
            try:
                self.connect()
                self.is_running = True
                while not self.stop:
                    if len(self.send_buffer) > 0:
                        self.client.send(self.send_buffer[:1024])
                        self.send_buffer = self.send_buffer[1024:]
                    # print("Flip")

                    try:
                        self.receive_buffer += self.client.recv(1024)
                    except BlockingIOError as ex:
                        pass
                    if len(self.receive_buffer) > 0:
                        self.process_message()
                    # print("Flop")

            except (socket.timeout, ConnectionError, ConnectionRefusedError, ConnectionResetError):
                print("Lost connection, attempting to reconnect")
                time.sleep(5)

    def process_message(self):
        if self.remaining_content == 0:
            # We have a new message
            try:
                header_byte_len, header_len, header = get_header(self.receive_buffer)
                self.header_length = header_byte_len + header_len
                self.remaining_content = header['content-length']
            except (KeyError, json.JSONDecodeError):
                print("Malformed packets received, clearing buffer")
                self.receive_buffer = bytes()

        if len(self.receive_buffer) >= self.header_length + self.remaining_content:
            # We have all the data now, and possibly more
            raw_message = self.receive_buffer[:self.header_length + self.remaining_content]
            self.receive_buffer = self.receive_buffer[len(raw_message):]
            self.header_length = 0
            self.remaining_content = 0
            self.message_handler(decode(raw_message))

class SocketServer:
    def __init__(self, address=("0.0.0.0", 65435)):
        self._address = address
        self._stop = False
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(False)
        self.server.bind(self._address)
        self.server.listen()
        self.selector = selectors.DefaultSelector()
        self.realtime_encoding = "UTF-8"
        self.selector.register(self.server, selectors.EVENT_READ, data=None)

    def run(self, message_handler, tick=None):
        while not self._stop:
            if tick:
                tick()
            events = self.selector.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    self.accept_wrapper(key.fileobj)
                else:
                    self.service_connection(key, mask, message_handler)

    def manual_run(self, message_handler, tick=None):
        if tick:
            tick()
        events = self.selector.select(timeout=1)
        for key, mask in events:
            if key.data is None:
                self.accept_wrapper(key.fileobj)
            else:
                self.service_connection(key, mask, message_handler)

    def stop(self):
        self._stop = True

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        log('accepted connection from', addr)
        conn.setblocking(False)
        data = types.SimpleNamespace(
            addr=addr, inb=b'', outb=b'', length=None, realtime=False)
        events = selectors.EVENT_READ
        self.selector.register(conn, events, data=data)

    def service_connection(self, key, mask, message_handler):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if data.realtime:
                self._realtime_receive(sock, data, recv_data, message_handler)
            else:
                try:
                    self._normal_receive(sock, data, recv_data, message_handler)
                except json.JSONDecodeError as ex:
                    print("Error decoding packet")
                    recv_data = None

    def _realtime_receive(self, sock, data, recv_data, message_handler):
        if data.realtime:
            if recv_data:
                message = recv_data.decode(self.realtime_encoding).strip()
                if "!:COMMAND:NORMAL:!" in message:
                    data.realtime = False
                    # self._normal_receive(sock, data, recv_data, message_handler)
                else:
                    return_message = {"message" : message,
                                      "type" : "realtime",
                                      "header" : None,
                                      "addr" : data.addr}
                    message_handler(return_message)
            else:
                print('closing connection to', data.addr)
                self.selector.unregister(sock)
                sock.close()
        else:
            self._normal_receive(sock, data, recv_data, message_handler)

    def _normal_receive(self, sock, data, recv_data, message_handler):
        if not data.realtime:
            if recv_data:
                if data.outb:
                    data.outb += recv_data
                    data.length -= len(recv_data)
                    if data.length == 0:
                        # We've received everything
                        _, _, header = get_header(data.outb)
                        return_message = {"message" : decode(data.outb),
                                      "type" : "json",
                                      "header" : header,
                                      "addr" : data.addr}
                        # print(f"Socket: {sock}")
                        message_handler(return_message, sock)
                        data.outb = b''
                        data.length = 0
                else:
                    header_byte_len, header_length, header = get_header(recv_data)
                    data.length = header_byte_len + header_length + header["content-length"]
                    data.outb += recv_data[:header_byte_len + header_length + header["content-length"]]
                    data.length -= len(recv_data[:header_byte_len + header_length + header["content-length"]])
                    if header["content-type"] == "COMMAND:REALTIME":
                        log("Realtime mode")
                        data.realtime = True
                        data.length = None
                        data.inb = b''
                        data.outb = b''
                    elif data.length < len(recv_data):
                        _, _, header = get_header(data.outb)
                        return_message = {"message" : decode(data.outb),
                                      "type" : "json",
                                      "header" : header,
                                      "addr" : data.addr}
                        message_handler(return_message, sock)
                        data.outb = b''
                        data.length = 0
            else:
                log('closing connection to', data.addr)
                self.selector.unregister(sock)
                sock.close()
        else:
            self._realtime_receive(sock, data, recv_data, message_handler)

import socket
import struct
import threading
import types
from datetime import datetime


def log(message):
    current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{current_date_time}] {message}')


class OSCClient:
    def __init__(self, listen_addr='0.0.0.0', listen_port=2050, callback: types.FunctionType = None):
        self.callback: types.FunctionType = callback
        self.listen_addr = listen_addr
        self.listen_port = listen_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.enabled = False

    def start(self):
        self.socket.bind((self.listen_addr, self.listen_port))
        log(f'Starting OSC server on {self.listen_addr}:{self.listen_port}')
        self.enabled = True
        while self.enabled:
            try:
                # Messages should be no longer than 1024 bytes (this is just a simple protocol after all)
                data, client_addr = self.socket.recvfrom(1024)
                client_thread = threading.Thread(target=self.handle_request, args=(data, client_addr))
                client_thread.setDaemon(True)
                client_thread.start()
            except OSError as err:
                log(err)
            except AssertionError as err:
                log(err)
            except KeyboardInterrupt:
                self.stop()

    def handle_request(self, data, client_addr):
        osc_message = OSCParser(data).parse()
        print(osc_message)
        print(data == osc_message.encode())
        if self.callback:
            self.callback((client_addr, osc_message))

    def stop(self):
        log('Shutting down OSC server')
        self.enabled = False
        self.socket.close()
        log('OSC server stopped')


class OSCMessage:
    def __init__(self, address: str, values: list):
        self.address: str = address
        self.values: list = values

    def __str__(self) -> str:
        return f'OSCMessage({self.address}: {self.values})'

    def encode(self) -> bytes:
        offset = 0
        # Encoding flag + address
        format_list = ['>', f'{len(self.address)}s']  # First item is always the big endian flag
        offset += len(self.address)
        pad_offset = 4 - (offset % 4)
        format_list.append(f'{pad_offset}x')
        # Types
        type_length = len(self.values) + 1
        format_list.append(f'{type_length}s')  # add 1 for the comma
        format_list.append(f'{4 - (type_length % 4)}x')
        type_list = [',']
        encoded_values = []
        for value in self.values:
            if type(value) == int:
                format_list.append('i')
                type_list.append('i')
                encoded_values.append(value)
            elif type(value) == float:
                format_list.append('f')
                type_list.append('f')
                encoded_values.append(value)
            elif type(value) == str:
                format_list.append(f'{len(value)}s')
                format_list.append(f'{4 - (len(value) % 4)}x')
                type_list.append('s')
                encoded_values.append(value.encode())
            else:
                raise Exception('Tried to encode unimplemented OSC type')
        pack_values = [self.address.encode(), ''.join(type_list).encode()]
        pack_values.extend(encoded_values)
        format_string = ''.join(format_list)
        return struct.pack(format_string, *pack_values)


class OSCParser:
    def __init__(self, data):
        self.offset = 0
        self.data = data

    def parse(self) -> OSCMessage:
        # First, calculate the address
        address = self._parse_string()
        data_types = self._parse_data_types()
        data_list = []
        for data_type in data_types:
            if data_type == 'i':
                data_list.append(self._parse_int())
            elif data_type == 'f':
                data_list.append(self._parse_float())
            elif data_type == 's':
                data_list.append(self._parse_string())
            else:
                raise Exception('Unimplemented OSC Type')
        return OSCMessage(address, data_list)

    def _parse_string(self) -> str:
        start_offset = self.offset
        while self.offset < len(self.data):
            if self.data[self.offset] != 0:
                self.offset += 1
            else:
                break
        return_string = self.data[start_offset:self.offset].decode()
        self.offset += (4 - (self.offset % 4))
        return return_string

    def _parse_data_types(self):
        # Ignore the first character, as that is always a comma
        data_types = self._parse_string()
        assert data_types[0] == ','
        data_types = data_types[1:].split()
        return data_types

    def _parse_int(self) -> int:
        self.offset += 4
        return struct.unpack_from('>i', self.data, self.offset - 4)[0]

    def _parse_float(self) -> float:
        self.offset += 4
        return struct.unpack_from('>f', self.data, self.offset - 4)[0]




from threading import Thread
from typing import Optional, Callable, Any, Iterable, Mapping
import json

from pidra.room.room import LivingRoom
from pidra.network.libnetwork import SocketServer, decode, encode
from time import sleep


class ServerThread(Thread):

    def __init__(self, address, port, update_function) -> None:
        super().__init__()
        self.server = SocketServer(address=(address, port))
        self.update_function = update_function

    def run(self) -> None:
        try:
            self.server.run(self.update_function)
        except KeyboardInterrupt:
            self.server.stop()

    def send(self, data):
        return self.server.server.send(data)


class Server:
    def __init__(self, address='0.0.0.0', port=25575):
        self.address = address
        self.port = port
        self.room = LivingRoom("Living Room")
        self.hdmi_thread = CECThread(self, self.hdmi_callback)
        self.cec_status = {}
        self.server_thread = ServerThread(address, port, self.message_handler)

    def parse_osc(self, message, sock):
        split_message = message.split('/')
        device = split_message[1] # offset by 1 because of initial slash
        property = split_message[2]
        intent = split_message[3]
        print(f"Device = '{device}', Property = '{property}, Intent = '{intent}'")
        # Audio System
        if device == "Audio":
            if property == "Volume":
                if intent == "?":
                    sock.send(encode("/Audio/Volume/" + str(self.room.audio.volume)))
                elif intent == "Up":
                    self.room.audio.volume_up()
                    sock.send(encode("OK"))
                elif intent == "Down":
                    self.room.audio.volume_down()
                    sock.send(encode("OK"))
            elif property == "Command":
                print("Sending command " + intent)
                self.room.audio.send_command(intent)
                sock.send(encode("OK"))

    def start(self):
        self.hdmi_thread.start()
        self.server_thread.start()
        print("Server started")

    def message_handler(self, message: dict, sock):
        received = message.get('message')
        print(message.get('message'))
        self.parse_osc(received, sock)

    def hdmi_callback(self, cec_dict):
        self.room.audio.volume = cec_dict['volume']
        self.cec_status = cec_dict
        print(cec_dict)



class CECThread(Thread):
    def __init__(self, server: Server, handler):
        super().__init__()
        self.server = server
        self.enabled = True
        self.handler = handler

    def run(self) -> None:
        while self.enabled:
            volume = self.server.room.cec.ask_for_volume()
            self.handler({
                "volume": volume,
                "source": None
            })
            sleep(5)

class SocketManager(Thread):
    def __init__(self):
        super().__init__()

    def run(self) -> None:
        super().run()


if __name__ == '__main__':
    server = Server()
    server.start()

from abc import ABCMeta, abstractmethod

from pidra.control.IR import IR
from pidra.control.tivo import TiVoRemote
from pidra.control.audio.audio import Receiver
from pidra.control.tv.tv import TV
from pidra.control.cec.cecclient import CECClient


class Room(metaclass=ABCMeta):
    def __init__(self, name):
        self.input = None
        self.name = name


class LivingRoom(Room):
    def __init__(self, name):
        super().__init__(name)
        self.stb = TiVoRemote("192.168.1.14")
        self.cec = CECClient()
        self.tv = TV("HisenseTV")
        self.audio = Receiver("Yamaha")
        self.generic = IR()

    def change_input(self, new_input):
        if new_input == "Fire TV" or new_input == "FireTV":
            self.audio.send_command("KEY_HDMI3")
            self.input = "Fire TV"
        elif new_input == "Blu-Ray":
            self.audio.send_command("KEY_BDDVD")
            self.input = "Blu-Ray"
        elif new_input == "TV":
            self.audio.send_command("KEY_TV")
            self.input = "TV"
        elif new_input == "Alexa":
            self.audio.send_command("KEY_RADIO")
            self.input = "Alexa"
        elif new_input == "PC":
            self.audio.send_command("KEY_HDMI4")
            self.input = "PC"


from abc import ABCMeta, abstractmethod
from pidra.control.IR import IR
from pidra.control.interfaces.common import *


class IRDevice(metaclass=ABCMeta):

    def __init__(self, device_name):
        self.ir_sender = IR()
        self.power = state.OFF
        self.device_name = device_name

    def power_on(self):
        if self.power == state.OFF:
            self.ir_sender.send_command(self.device_name, "KEY_POWER")
            self.power = state.ON
            return True
        else:
            return False

    def power_off(self):
        if self.power == state.ON:
            self.ir_sender.send_command(self.device_name, "KEY_POWER")
            self.power = state.OFF
            return True
        else:
            return False

    def send_command(self, command):
        if self.ir_sender.send_command(self.device_name, command):
            return True
        else:
            return False

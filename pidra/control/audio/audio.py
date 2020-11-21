from pidra.control.IR import IR
from pidra.control.interfaces.common import *
from pidra.control.cec.cecclient import CECClient
from pidra.control.interfaces.IRDevice import IRDevice


class Receiver(IRDevice):

    def __init__(self, device_name):
        super().__init__(device_name)
        self.volume = 0

    def volume_up(self):
        self.ir_sender.send_command(self.device_name, "KEY_VOLUMEUP")
        self.volume += 1

    def volume_down(self):
        self.ir_sender.send_command(self.device_name, "KEY_VOLUMEDOWN")
        self.volume -= 1
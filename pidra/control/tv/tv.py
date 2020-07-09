from pidra.control.IR import IR
from pidra.control.interfaces.common import *
from pidra.control.interfaces.IRDevice import IRDevice
from pidra.control.cec.cecclient import CECClient


class TV(IRDevice):

    def __init__(self, device_name):
        super().__init__(device_name)

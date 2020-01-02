from abc import ABCMeta, abstractmethod
from pidra.interfaces.common import state

class STB(metaclass=ABCMeta):
    def __init__(self):
        pass

    def toggle_power(self):
        if self.power == state.ON:
            self.power_off()
        else:
            self.power_on()

    @property
    @abstractmethod
    def power(self):
        pass

    @property
    @abstractmethod
    def channel(self):
        pass

    @abstractmethod
    def set_channel(self, channel):
        # Code for changing the channel
        pass

    @abstractmethod
    def power_on(self):
        pass

    @abstractmethod
    def power_off(self):
        pass

    @abstractmethod
    def send_command(self, command):
        pass
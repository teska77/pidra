from abc import ABCMeta, abstractmethod
from pidra.control.interfaces.common import state


class STB(metaclass=ABCMeta):
    def __init__(self):
        self.commands = {
            "power_on": self.power_on,
            "power_off": self.power_off,
            "power": self.toggle_power
        }

    def toggle_power(self):
        if self.power == state.ON:
            self.power_off()
        else:
            self.power_on()
        return self.power

    def send_command(self, command):
        if command in self.commands:
            print(command)
            executed_command = self.commands.get(command)()
            if executed_command:
                return executed_command
            else:
                return True
        else:
            return False

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
    def press(self, button):
        pass
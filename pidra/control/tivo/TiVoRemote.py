from pidra.control.interfaces.STB import STB
from pidra.control.interfaces.common import state
from pidra.control.tivo import utils


class TiVoRemote(STB):

    def __init__(self, host, port=31339):
        print("Ready")
        self.tivo = utils.TiVoConnection(host, port)
        super().__init__()
        default_commands = self.commands
        self.commands = {**default_commands,
                         "channel_up": self.channel_up,
                         "channel_down": self.channel_down,
                         "go_home": self.go_home,
                         "go_guide": self.go_guide,
                         "go_tv": self.go_tv,
                         "go_my_shows": self.go_my_shows,
                         "up": self.up,
                         "down": self.down,
                         "left": self.left,
                         "right": self.right,
                         "enter": self.enter,
                         "back": self.back,
                         "play": self.play,
                         "pause": self.pause,
                         "rewind": self.rewind,
                         "forward": self.forward,
                         "next": self.next,
                         "previous": self.previous,
                         "stop": self.stop
                         }

    # Buttons
    def up(self):
        self.press("UP")

    def down(self):
        self.press("DOWN")

    def left(self):
        self.press("LEFT")

    def right(self):
        self.press("RIGHT")

    def enter(self):
        self.press("SELECT")

    def back(self):
        self.press("BACK")

    def play(self):
        self.press("PLAY")

    def pause(self):
        self.press("PAUSE")

    def rewind(self):
        self.press("REVERSE")

    def forward(self):
        self.press("FORWARD")

    def next(self):
        self.press("ADVANCE")

    def previous(self):
        self.press("REPLAY")

    def stop(self):
        self.press("STOP")

    @property
    def channel(self):
        try:
            return int(self.tivo.channel)
        except TypeError:
            return None

    @property
    def power(self):
        if self.tivo.powered_on:
            return state.ON
        else:
            return state.OFF

    def set_channel(self, channel):
        old_channel = channel
        # Check if channel is an int, and convert to string, adding a zero.
        channel_no = str(channel).zfill(
            4)  # TiVo expects a 4-digit channel number, despite UK TiVo having less than 999 channels.
        self.tivo.setChannel(channel_no)
        if old_channel != channel:
            return True
        else:
            return False

    def power_on(self):
        self.tivo.power_on()
        # return True

    def power_off(self):
        self.tivo.power_off()
        # return True

    def press(self, button):
        self.tivo.sendIRCode(button)
        # return True

    # Essential buttons

    def channel_up(self):
        self.press("CHANNELUP")
        return True

    def channel_down(self):
        self.press("CHANNELDOWN")
        return True

    # Custom views
    def go_home(self):
        self.tivo.sendTeleport(utils.TeleportType.TIVO)
        # return True

    def go_tv(self):
        self.tivo.sendTeleport(utils.TeleportType.LIVETV)
        # return True

    def go_guide(self):
        self.tivo.sendTeleport(utils.TeleportType.GUIDE)
        # return True

    def go_my_shows(self):
        self.tivo.sendTeleport(utils.TeleportType.NOWPLAYING)
        # return True

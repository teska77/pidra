from pidra.interfaces.STB import STB
from pidra.interfaces.common import state
from pidra.tivo import utils

class TiVoRemote(STB):
    def __init__(self, host, port=31339):
        super().__init__()
        self.tivo = utils.TiVoConnection(host, port)

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
        # Check if channel is an int, and convert to string, adding a zero.
        channel_no = str(channel).zfill(4) # TiVo expects a 4-digit channel number, despite UK TiVo having less than 999 channels.
        self.tivo.setChannel(channel_no)

    def power_on(self):
        self.tivo.power_on()

    def power_off(self):
        self.tivo.power_off()

    def press(self, button):
        self.tivo.sendIRCode(button)

    # Essential buttons

    def channel_up(self):
        self.press("CHANNELUP")

    def channel_down(self):
        self.press("CHANNELDOWN")
    
    # Custom views

    def go_home(self):
        self.tivo.sendTeleport(utils.TeleportType.TIVO)

    def go_tv(self):
        self.tivo.sendTeleport(utils.TeleportType.LIVETV)

    def go_guide(self):
        self.tivo.sendTeleport(utils.TeleportType.GUIDE)

    def go_my_shows(self):
        self.tivo.sendTeleport(utils.TeleportType.NOWPLAYING)
import os
from subprocess import Popen, PIPE
import pprint


class CECClient:
    def __init__(self):
        self.cec_command = "cec-client -s -d 8"

    def send_command(self, command):
        proc = Popen(self.cec_command.split(' '), stdout=PIPE, stdin=PIPE)
        print(self.cec_command)
        return proc.communicate(input=command.encode())

    def ask_for_volume(self):
        volume_output = self.send_command("tx F5:71")[0].decode()
        volume = volume_output.split("7a:")[1]
        # Split after 7a: as that is the CEC code for audio status response, the final two hex digits are the volume.
        # We then take the two characters after this split, as to trim out all the other logging information.
        return int(volume[:2], 16)


if __name__ == '__main__':
    client = CECClient()
    print(client.ask_for_volume())

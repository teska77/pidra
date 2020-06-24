import os
from subprocess import Popen, PIPE


class CECClient:
    def __init__(self):
        self.cec_command = "cec-client -s -d 8"

    def send_command(self, command):
        proc = Popen(self.cec_command.split(' '), stdout=PIPE, stdin=PIPE)
        print(self.cec_command)
        return proc.communicate(input=command.encode())

    def ask_for_volume(self):
        volume_output = self.send_command("tx F5:71")[0].decode()
        volume = volume_output.split("7a:")
        return int(volume[1], 16)


if __name__ == '__main__':
    client = CECClient()
    print(client.ask_for_volume())

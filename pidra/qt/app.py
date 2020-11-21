import typing, time, datetime

import PySide2
import qdarkstyle
from PySide2 import QtWidgets, QtGui
from PySide2.QtCore import QThread
from PySide2.QtWidgets import QWidget, QApplication, QDialog

from pidra.qt.ui.main_ui import *
from pidra.network.libnetwork import SocketClient, encode, decode, LightSocketClient


class ClockThread(QThread):

    def __init__(self, tick_function):
        super().__init__()
        self.enabled = True
        self.tick_function = tick_function

    def run(self):
        while self.enabled:
            self.tick_function()
            time.sleep(1)


class QueryThread(QThread):
    def __init__(self, tick_function):
        super().__init__()
        self.enabled = True
        self.tick_function = tick_function

    def run(self):
        while self.enabled:
            self.tick_function()
            time.sleep(2)


class NetworkThread(QThread):
    def __init__(self, update_function):
        super().__init__()
        self.client = LightSocketClient(('192.168.1.17', 25575), update_function)

    def run(self):
        self.client.connect()

    def send(self, message):
        self.client.send(message)


class PidraApp(QDialog):
    def __init__(self):
        super(PidraApp, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.volume_meter = 0
        self.ui.buttonVolumeUp.pressed.connect(lambda: self.change_volume(self.ui.buttonVolumeUp))
        self.ui.buttonVolumeDown.pressed.connect(lambda: self.change_volume(self.ui.buttonVolumeDown))
        self.client = LightSocketClient(('192.168.1.17', 25575), self.receive_message)
        # self.network_thread = NetworkThread(self.receive_message)
        # self.network_thread.start()
        self.query_thread = QueryThread(self.query)
        self.query_thread.start()
        self.clock_timer = ClockThread(self.update_time)
        self.clock_timer.start()

    def query(self):
        if self.client:
            self.client.send(encode('/Audio/Volume/?'))

    def update_time(self):
        self.ui.labelClock.setText(datetime.datetime.now().strftime("%H:%M:%S"))

    def receive_message(self, message):
        print(message)
        if "/Audio/Volume" in message:
            self.volume_meter = int(message.replace("/Audio/Volume/", ''))
            self.ui.lcdVolume.display(self.volume_meter)

    def change_volume(self, button):
        if button == self.ui.buttonVolumeDown:
            self.volume_meter -= 1
            self.client.send(encode('/Audio/Volume/Down'))
        elif button == self.ui.buttonVolumeUp:
            self.volume_meter += 1
            self.client.send(encode('/Audio/Volume/Up'))
        self.ui.lcdVolume.display(self.volume_meter)

if __name__ == '__main__':

    import sys, platform

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    window = PidraApp()

    if platform.system() == 'Linux':
        window.showFullScreen()
    else:
        window.show()

    sys.exit(app.exec_())
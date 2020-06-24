import socket
import logging
import select
import threading
import time
# Based on an adaptation of python-tivo, available at: https://github.com/mattjgalloway/python-tivo

def IsChannelStatus(response):
    return response["type"] == ResponseType.CH_STATUS


def IsInvalidKey(response):
    return response["type"] == ResponseType.INVALID_KEY


def FullChannelName(response):
    if not IsChannelStatus(response):
        return None

    fullChannel = response['channel']
    if response['subChannel']:
        fullChannel += "-"
        fullChannel += response["subChannel"]

    return fullChannel


class TiVoError(Exception):
    pass


class TiVoSocketError(Exception):
    pass


class ThreadedSocket(object):
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._data = b""
        self._timeoutLock = threading.Lock()
        self._timeout = None
        self._connect()

    def send(self, data):
        self._sock.sendall(data)

    def wait(self, timeout=0):
        self._timeoutLock.acquire()
        self._timeout = time.time() + timeout
        self._timeoutLock.release()
        self._recvThread.join()
        return self._data

    def _connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(10)
        self._sock.connect((self._host, self._port))
        self._sock.setblocking(0)
        self._recvThread = threading.Thread(target=self._receive)
        self._recvThread.start()

    def _receive(self):
        while True:
            try:
                self._timeoutLock.acquire()
                timeout = self._timeout
                self._timeoutLock.release()
                if timeout and time.time() >= timeout:
                    raise TimeoutError()

                ready = select.select([self._sock], [], [], 0.5)
                if ready[0]:
                    data = self._sock.recv(4096)
                    self._data += data
            except:
                self._sock.close()
                return False


class TiVoConnection(object):
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._sendCommandsLock = threading.Lock()

    def sendCommands(self, commands):
        try:
            self._sendCommandsLock.acquire()

            sock = ThreadedSocket(self._host, self._port)

            if len(commands) > 0:
                # Leave some time to receive the first message before sending anything
                time.sleep(0.1)

                for command in commands:
                    if command.startswith("WAIT "):
                        try:
                            timeToSleep = float(command[5:])
                            time.sleep(timeToSleep)
                        except ValueError:
                            pass
                    else:
                        fullCommand = command + "\r"
                        sock.send(fullCommand.encode("utf-8"))
                        time.sleep(0.1)

            allData = sock.wait(0.1)

            if len(allData) == 0:
                return []

            allData = allData.decode("utf-8")
            allResponses = allData.split("\r")
            allResponses = filter(None, allResponses)
            parsedResponses = list(map(self._parseResponse, allResponses))
            return parsedResponses
        except:
            raise TiVoSocketError()
        finally:
            self._sendCommandsLock.release()

    @staticmethod
    def _readFromSocket(sock, timeout):
        allData = b""
        begin = time.time()
        while True and time.time() - begin < timeout:
            ready = select.select([sock], [], [], timeout)
            print("Ready {}".format(ready))
            if ready[0]:
                data = sock.recv(4096)
                allData += data
            else:
                break
        return allData

    @property
    def powered_on(self):
        responses = self.sendCommands([])
        return len(responses) > 0

    @property
    def channel(self):
        responses = self.sendCommands([])
        if len(responses) == 0:
            return None
        lastResponse = responses[0]
        return FullChannelName(lastResponse)

    def power_on(self):
        if not self.powered_on:
            self.sendCommands(["IRCODE STANDBY"])

    def power_off(self):
        if self.powered_on:
            self.sendCommands(["IRCODE STANDBY", "WAIT 0.5", "IRCODE STANDBY"])

    def setChannel(self, channel):
        responses = self.sendCommands(["SETCH " + channel])
        if len(responses) == 0:
            return False

        lastResponse = responses[-1]
        if not IsChannelStatus(lastResponse):
            return False

        return lastResponse["channel"] == channel.zfill(4)

    def forceChannel(self, channel):
        responses = self.sendCommands(["FORCECH " + channel])
        if len(responses) == 0:
            return False

        lastResponse = responses[-1]
        if not IsChannelStatus(lastResponse):
            return False

        return lastResponse["channel"] == channel.zfill(4)

    def sendIRCode(self, code):
        return self.sendCommands(["IRCODE " + code])

    def sendKeyboard(self, code):
        return self.sendCommands(["KEYBOARD " + code])

    def sendTeleport(self, code):
        return self.sendCommands(["TELEPORT " + code])

    @staticmethod
    def _parseResponse(message):
        split = message.split(" ")
        type = split[0]
        response = {
            "raw": message,
            "type": type
        }

        if type == ResponseType.CH_STATUS:
            response["channel"] = split[1]
            response["reason"] = split[-1]
            response["subChannel"] = split[2] if len(split) == 4 else None
        elif type == ResponseType.CH_FAILED:
            response["reason"] = split[1]

        return response

# Constants


class ResponseType():
    CH_STATUS = "CH_STATUS"
    CH_FAILED = "CH_FAILED"
    LIVETV_READY = "LIVETV_READY"
    MISSING_TELEPORT_NAME = "MISSING_TELEPORT_NAME"
    INVALID_KEY = "INVALID_KEY"


class ChannelStatusReason():
    LOCAL = "LOCAL"
    REMOTE = "REMOTE"
    RECORDING = "RECORDING"


class ChannelSetFailureReason():
    NO_LIVE = "NO_LIVE"
    MISSING_CHANNEL = "MISSING_CHANNEL"
    MALFORMED_CHANNEL = "MALFORMED_CHANNEL"
    INVALID_CHANNEL = "INVALID_CHANNEL"


class IRCodeCommand():
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    SELECT = "SELECT"
    TIVO = "TIVO"
    LIVETV = "LIVETV"
    GUIDE = "GUIDE"
    INFO = "INFO"
    EXIT = "EXIT"
    THUMBSUP = "THUMBSUP"
    THUMBSDOWN = "THUMBSDOWN"
    CHANNELUP = "CHANNELUP"
    CHANNELDOWN = "CHANNELDOWN"
    MUTE = "MUTE"
    VOLUMEUP = "VOLUMEUP"
    VOLUMEDOWN = "VOLUMEDOWN"
    TVINPUT = "TVINPUT"
    VIDEO_MODE_FIXED_480i = "VIDEO_MODE_FIXED_480i"
    VIDEO_MODE_FIXED_480p = "VIDEO_MODE_FIXED_480p"
    VIDEO_MODE_FIXED_720p = "VIDEO_MODE_FIXED_720p"
    VIDEO_MODE_FIXED_1080i = "VIDEO_MODE_FIXED_1080i"
    VIDEO_MODE_HYBRID = "VIDEO_MODE_HYBRID"
    VIDEO_MODE_HYBRID_720p = "VIDEO_MODE_HYBRID_720p"
    VIDEO_MODE_HYBRID_1080i = "VIDEO_MODE_HYBRID_1080i"
    VIDEO_MODE_NATIVE = "VIDEO_MODE_NATIVE"
    CC_ON = "CC_ON"
    CC_OFF = "CC_OFF"
    OPTIONS = "OPTIONS"
    ASPECT_CORRECTION_FULL = "ASPECT_CORRECTION_FULL"
    ASPECT_CORRECTION_PANEL = "ASPECT_CORRECTION_PANEL"
    ASPECT_CORRECTION_ZOOM = "ASPECT_CORRECTION_ZOOM"
    ASPECT_CORRECTION_WIDE_ZOOM = "ASPECT_CORRECTION_WIDE_ZOOM"
    PLAY = "PLAY"
    FORWARD = "FORWARD"
    REVERSE = "REVERSE"
    PAUSE = "PAUSE"
    SLOW = "SLOW"
    REPLAY = "REPLAY"
    ADVANCE = "ADVANCE"
    RECORD = "RECORD"
    NUM0 = "NUM0"
    NUM1 = "NUM1"
    NUM2 = "NUM2"
    NUM3 = "NUM3"
    NUM4 = "NUM4"
    NUM5 = "NUM5"
    NUM6 = "NUM6"
    NUM7 = "NUM7"
    NUM8 = "NUM8"
    NUM9 = "NUM9"
    ENTER = "ENTER"
    CLEAR = "CLEAR"
    ACTION_A = "ACTION_A"
    ACTION_B = "ACTION_B"
    ACTION_C = "ACTION_C"
    ACTION_D = "ACTION_D"
    BACK = "BACK"
    WINDOW = "WINDOW"


class KeyboardCommand():
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"
    I = "I"
    J = "J"
    K = "K"
    L = "L"
    M = "M"
    N = "N"
    O = "O"
    P = "P"
    Q = "Q"
    R = "R"
    S = "S"
    T = "T"
    U = "U"
    V = "V"
    W = "W"
    X = "X"
    Y = "Y"
    Z = "Z"
    MINUS = "MINUS"
    EQUALS = "EQUALS"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    BACKSLASH = "BACKSLASH"
    SEMICOLON = "SEMICOLON"
    QUOTE = "QUOTE"
    COMMA = "COMMA"
    PERIOD = "PERIOD"
    SLASH = "SLASH"
    BACKQUOTE = "BACKQUOTE"
    SPACE = "SPACE"
    KBDUP = "KBDUP"
    KBDDOWN = "KBDDOWN"
    KBDLEFT = "KBDLEFT"
    KBDRIGHT = "KBDRIGHT"
    PAGEUP = "PAGEUP"
    PAGEDOWN = "PAGEDOWN"
    HOME = "HOME"
    END = "END"
    CAPS = "CAPS"
    LSHIFT = "LSHIFT"
    RSHIFT = "RSHIFT"
    INSERT = "INSERT"
    BACKSPACE = "BACKSPACE"
    DELETE = "DELETE"
    KBDENTER = "KBDENTER"
    STOP = "STOP"
    VIDEO_ON_DEMAND = "VIDEO_ON_DEMAND"


class TeleportType():
    TIVO = "TIVO"
    LIVETV = "LIVETV"
    GUIDE = "GUIDE"
    NOWPLAYING = "NOWPLAYING"
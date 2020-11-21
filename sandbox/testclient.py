from pidra.server.libnetwork import decode, encode
import socket
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect(('192.168.1.17', 25575))
socket.send(encode('getVolume()', 'volumereq'))

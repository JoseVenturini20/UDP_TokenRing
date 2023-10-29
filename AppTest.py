import socket

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.sendto(b'Hello', ('localhost', 5000))
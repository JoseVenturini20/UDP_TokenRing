import socket

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.sendto(b'9000', ('localhost', 5000))
#socket.sendto(b'7777:ACK;Bob:Mary;19385749;Oi pessoal!', ('localhost', 5000))

#socket.sendto(b'7777:NACK;Jose;B;4157704578;Hello', ('localhost', 5000))
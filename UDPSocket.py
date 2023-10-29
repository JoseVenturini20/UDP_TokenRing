import socket

class UDPSocket:
    def __init__(self, port):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', self.port))

    def send(self, data, address):
        self.socket.sendto(data, address)

    def recv(self):
        try:
            data, address = self.socket.recvfrom(1024)
            return data
        except socket.error:
            print(f"Socket error: {e}")
            return None

    def close(self):
        self.socket.close()
import threading
from UDPSocket import UDPSocket
import queue

class TokenRing:
    def __init__(self):
        self.__UDPSocket = UDPSocket(5000)
        threading.Thread(target=self.__receive_data).start()
        self.__configure()
        self.__queue = queue.Queue()

    def __receive_data(self):
        while True:
            data = self.__UDPSocket.recv()
            if data:
                print(data.decode('utf-8'))
            else:
                print('No data received')
    
    def __configure(self):
        with open('config.txt', 'r') as file:
            data = file.readlines()
            self.__right_ip = data[0].split(':')[0].strip()
            self.__right_port = int(data[0].split(':')[1].strip())
            self.__right_nickname = data[1].strip()
            self.__token_time = int(data[2].strip())
            self.__token = bool(data[3].strip())

    def __decode_data(self, data):
        pass

    def __calculate_crc(self, data):
        pass

    def __check_crc(self, data):
        pass

    def __retransmit_message(self, data):
        pass

    def __acknowledge_message(self, data):
        pass

    def __send_token(self):
        pass

    def __remove_token(self):
        pass

    def __token_timeout_check(self):
        pass

    def __enqueue_message(self, message):
        pass

    def __dequeue_message(self):
        pass
        
    def __send(self, data):
        self.__UDPSocket.send(data, (self.__right_ip, self.__right_port))

    def send_message(self, message, nickname):
        pass

    def introduce_error(self):
        pass

tk = TokenRing()

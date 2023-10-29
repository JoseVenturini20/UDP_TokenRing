import threading
from Temp import Temp
from UDPSocket import UDPSocket
import queue
class TokenRing:
    def __init__(self):
        self.__UDPSocket = UDPSocket(5000)
        threading.Thread(target=self.__receive_data).start()
        self.__configure()
        self.__queue = queue.Queue()
        self.__temp_token_management = Temp(5)
        self.__temp_with_token = Temp(self.__token_time)
        self.__token_holder_flag = False
        self.__ack_event_thread = None
        self.__ack_event = threading.Event()
        self.__last_message = None

    def __receive_data(self):
        while True:
            data = self.__UDPSocket.recv()
            if data:
                self.__decode_data(data.decode("utf-8"))
            else:
                print('No data received')
    
    def __configure(self):
        with open('config.txt', 'r') as file:
            data = file.readlines()
            self.__right_ip = data[0].split(':')[0].strip()
            self.__right_port = int(data[0].split(':')[1].strip())
            self.__right_nickname = data[1].strip()
            self.__token_time = int(data[2].strip())
            self.__token = data[3].strip() == 'true'

    def __control_token(self):
        def remove_token():
            print('Token removed')

        def token_timeout():
            print('Token timeout')
            self.__send_token()

        def multiple_tokens():
            remove_token()
        
        if self.__temp_token_management.is_running():
            multiple_tokens()
        else: 
            self.__temp_token_management.start(token_timeout)
            self.__is_token_holder = True

    def __decode_data(self, data):
        if data == '9000':
            if (self.__token):
                self.__control_token()
            else:
                self.__is_token_holder = True
                #self.__temp_with_token.start(self.__send_token)
        else:
            msg = data.split(';')
            ack = msg[0].split(':')[1]
            if (ack == 'ACK' or ack == 'NACK' or 'naoexiste'):
                self.__ack_event.set()

    def __calculate_crc(self, data):
        pass

    def __check_crc(self, data):
        pass

    def __retransmit_message(self, data):
        pass

    def __wait_for_acknowledgement(self):
        self.__ack_event.wait()
        print('ACK received')
        self.__last_message = None
        self.__ack_event.clear()

    @property
    def __is_token_holder(self):
        return self.__token_holder_flag

    @__is_token_holder.setter
    def __is_token_holder(self, value):
        if value and not self.__token_holder_flag: 
            print('Token holder')
            self.__token_holder_flag = value
            self.__ack_event_thread = threading.Thread(target=self.__send_message_when_token_holder)
            self.__ack_event_thread.start()

    def __send_message_when_token_holder(self):
        print('Sending message')
        if not self.__queue.empty():
            self.__send(self.__queue.get())
            self.__wait_for_acknowledgement()
            self.__temp_with_token.start(self.__send_token)

    def __send_token(self):
        self.__is_token_holder = False
        self.__send(b'9000')

    def __enqueue_message(self, message):
        self.__queue.put(message)

        
    def __send(self, data):
        print('Sending data', data)
        self.__last_message = data
        self.__UDPSocket.send(data, (self.__right_ip, self.__right_port))

    def send_message(self, message, nickname):
        self.__enqueue_message(message)

    def introduce_error(self):
        pass

tk = TokenRing()
tk.send_message(b'7777:ACK;Bob:Mary;19385749;Oi pessoal!', 'Bob')
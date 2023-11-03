import threading
import zlib
from Temp import  Temp
from UDPSocket import UDPSocket
import queue

class DisplayManager:
    def __init__(self):
        self.statuses = {}
        self.lock = threading.Lock()

    def update_status(self, message, temp_instance):
        with self.lock:
            self.statuses[temp_instance] = message
            self.refresh_display()

    def refresh_display(self):
        output = ' | '.join(status for status in self.statuses.values())
        print(output, end='\r', flush=True)
class TokenRing:
    def __init__(self, display_manager):
        self.display_manager = display_manager
        self.__UDPSocket = UDPSocket(5000)
        threading.Thread(target=self.__receive_data).start()
        self.__configure()
        self.__queue = queue.Queue()
        self.__temp_token_management_timeout = Temp(10, alignment=0, text='Timeout: ', update_callback=self.display_manager.update_status)
        self.__temp_token_management_multiple_tokens = Temp(8, alignment=0, text='Multiple tokens: ', update_callback=self.display_manager.update_status)
        self.__temp_with_token = Temp(self.__token_time)
        self.__token_holder_flag = False
        self.__ack_event_thread = None
        self.__ack_event = threading.Event()
        self.__last_message = None
        if (self.__token):
            self.__temp_with_token.start(self.__send_token)

    def __receive_data(self):
        while True:
            data = self.__UDPSocket.recv()
            print('Received data', data)
            if data:
                self.__decode_data(data.decode("utf-8"))
            else:
                print('No data received')
    
    def __configure(self):
        with open('config.txt', 'r') as file:
            data = file.readlines()
            self.__right_ip = data[0].split(':')[0].strip()
            self.__right_port = int(data[0].split(':')[1].strip())
            self.__my_nickname = data[1].strip()
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
        
        print(self.__temp_token_management_multiple_tokens.is_running())
        if self.__temp_token_management_multiple_tokens.is_running():
            multiple_tokens()
        else: 
            self.__is_token_holder = True

    def __decode_data(self, data):
        if data == '9000':
            if (self.__token):
                self.__control_token()
            else:
                self.__is_token_holder = True
                #self.__temp_with_token.start(self.__send_token)
        else:
            msg = data.split(':')
            msg = msg[1].split(';')
            ack = msg[0]
            origin = msg[1]
            destination = msg[2]
            crc = msg[3]
            msg_content = msg[4]
            if (origin == self.__my_nickname):
                if (ack.lower() == 'nack'):
                    self.__ack_event.set()
                    print('Message not acknowledged', msg)
                    self.__enqueue_message(self.__last_message)
                elif (ack.lower() =='naoexiste'):
                    self.__ack_event.set()
                    print('Destination unreachable', msg)
                elif (ack.lower() == 'ack'):
                    self.__ack_event.set()
                    print('Message Acknowledged', msg)
            elif(destination == self.__my_nickname):
                if(self.__check_crc(msg_content, int(crc))):
                    print('Message received', msg)
                    self.__send('7777:ACK;{};{};{};{}'.format(origin, destination, crc, msg_content).encode('utf-8'))
                else:
                    print('Message corrupted', msg)
                    self.__send('7777:NACK;{};{};{};{}'.format(origin, destination, crc, msg_content).encode('utf-8'))
            else:
                self.__send(data.encode('utf-8'))

    def __calculate_crc(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        return zlib.crc32(data)

    def __check_crc(self, data, expected_crc):
        calculated_crc = self.__calculate_crc(data)
        return calculated_crc == expected_crc

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
        else:
            self.__token_holder_flag = value

    def __send_message_when_token_holder(self):
        print('Sending message')
        if not self.__queue.empty():
            self.__send(self.__queue.get())
            self.__temp_with_token.start(self.__send_token)
            self.__wait_for_acknowledgement()
        else: 
            self.__temp_with_token.start(self.__send_token)

    def __send_token(self):
        self.__is_token_holder = False
        print("token holder flag", self.__token_holder_flag)
        if (self.__token):
            self.__temp_token_management_timeout.start(callback=self.__send_token)
            self.__temp_token_management_multiple_tokens.start()
        self.__send(b'9000')

    def __enqueue_message(self, message):
        self.__queue.put(message)
        
    def __send(self, data):
        print('Sending data', data)
        self.__last_message = data
        self.__UDPSocket.send(data, (self.__right_ip, self.__right_port))

    def send_message(self, message, nickname):
        msg = '7777:naoexiste;{};{};{};{}'.format(self.__my_nickname, nickname, self.__calculate_crc(message), message)
        self.__enqueue_message(msg.encode('utf-8'))

    def introduce_error(self):
        pass

if __name__ == "__main__":
    display_manager = DisplayManager()
    
    # TokenRing será atualizado para aceitar display_manager como parâmetro
    tk = TokenRing(display_manager)


while True:
    to = input('To: ')
    msg = input('Message: ')
    tk.send_message(msg, to)
    
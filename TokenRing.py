import threading
import zlib
from Temp import  Temp
from UDPSocket import UDPSocket
import queue
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import clear
import curses
class DisplayManager:
    def __init__(self):
        self.statuses = {}
        self.lock = threading.Lock()
        self.progress = Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.description]{task.description}"),
        )
        self.token_holder = Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.description]{task.description}"),
        )
        self.table = Table.grid(expand=True)
        self.table.add_column(justify="right")
        self.live = Live(self.table, refresh_per_second=10)
        self.tasks = {}
        self.task_token_holder = {}
        self.task_input = {}
        self.live.start()

    def update_status(self, message, temp_instance):
        with self.lock:
            # Update the task's progress
            task = self.tasks.get(temp_instance)
            if task is None:
                task = self.progress.add_task(description=message, total=100)
                self.tasks[temp_instance] = task
            else:
                self.progress.update(task, description=message)

            self.refresh_display()

    def update_token_holder(self, message, temp_instance):
        with self.lock:
            # Update the task's progress
            task = self.task_token_holder.get(temp_instance)
            if task is None:
                task = self.token_holder.add_task(description=message, total=100)
                self.task_token_holder[temp_instance] = task
            else:
                self.token_holder.update(task, description=message)

            self.refresh_display()

    def refresh_display(self):
        # Redraw the table with the updated progress
        self.table = Table.grid(expand=True)
        self.table.add_column(justify="right")
        self.table.add_row(
            Panel.fit(self.progress, title="Status Token Manager", border_style="green", padding=(1, 2), width=60)
        )
        self.table.add_row(
            Panel.fit(self.token_holder, title="Token Holder", border_style="red", padding=(1, 2), width=60)
        )
        self.live.update(self.table)
        

class TokenRing:
    def __init__(self, display_manager):
        self.display_manager = display_manager
        self.__UDPSocket = UDPSocket(5000)
        threading.Thread(target=self.__receive_data).start()
        self.__configure()
        self.__queue = queue.Queue()
        self.__temp_token_management_timeout = Temp(10, alignment=0, text='Timeout: ', update_callback=self.display_manager.update_status)
        self.__temp_token_management_multiple_tokens = Temp(8, alignment=0, text='Multiple tokens: ', update_callback=self.display_manager.update_status)
        self.__temp_with_token = Temp(self.__token_time, alignment=0, text='Token: ', update_callback=self.display_manager.update_token_holder)
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
            if (destination.lower() == 'todos'):
                print('Message received', msg)
                self.__send(data.encode('utf-8'))
            elif (origin == self.__my_nickname):
                if (ack.lower() == 'nack'):
                    self.__ack_event.set()
                    print('Message not acknowledged', msg)
                    self.__enqueue_message(self.__last_message)
                    # esta errado tem que ser no começo
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
        self.display_manager.update_token_holder('Token Holder: {}'.format(value), self.__temp_token_management_timeout)
        if value and not self.__token_holder_flag: 
            print('Token holder')
            self.__token_holder_flag = value
            self.__ack_event_thread = threading.Thread(target=self.__send_message_when_token_holder)
            self.__ack_event_thread.start()
            if (self.__token):
                self.__temp_token_management_multiple_tokens.stop()
                self.__temp_token_management_timeout.stop()
            if self.__temp_token_management_timeout.is_running():
                self.__temp_token_management_timeout.stop()
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

    def send_message(self, message, nickname = 'TODOS'):
        msg = '7777:naoexiste;{};{};{};{}'.format(self.__my_nickname, nickname, self.__calculate_crc(message), message)
        self.__enqueue_message(msg.encode('utf-8'))

    def introduce_error(self):
        pass

if __name__ == "__main__":
    display_manager = DisplayManager()
    
    tk = TokenRing(display_manager)




import random
import threading
import zlib
from Temp import  Temp
from UDPSocket import UDPSocket
import queue
import tkinter as tk
from tkinter import END, ttk
class DisplayManager:
    def start_gui_loop(self):
        self.root.mainloop()

    class TextRedirector(object):
        def __init__(self, widget):
            self.widget = widget

        def write(self, string):
            self.widget.config(state='normal')
            self.widget.insert(END, string)
            self.widget.see(END)
            self.widget.config(state='disabled')

        def flush(self):
            pass

    def __init__(self):
        BG_COLOR = "#333333"
        FG_COLOR = "#CCCCCC"
        LOG_BG = "#222222"
        BUTTON_BG = "#555555"

        self.style = ttk.Style()
        self.style.configure('TLabel', background=BG_COLOR, foreground=FG_COLOR)
        self.style.configure('TEntry', background=BG_COLOR, foreground=FG_COLOR)
        self.style.configure('TButton', background=BUTTON_BG, foreground=FG_COLOR)
        self.style.configure('TFrame', background=BG_COLOR)

        self.root = tk.Tk()
        self.root.title("Token Ring")
        self.root.geometry('1200x500') 
        self.root.configure(bg=BG_COLOR)

        self.frame_logs = ttk.Frame(self.root, padding="3")
        self.frame_logs.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.frame_controls = ttk.Frame(self.root, padding="3")
        self.frame_controls.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.root.grid_columnconfigure(1, weight=0)

        self.text_widget_label = ttk.Label(self.frame_logs, text="Logs")
        self.text_widget_label.pack(fill='x')

        self.text_widget = tk.Text(self.frame_logs, wrap='word', bg=LOG_BG, fg=FG_COLOR)
        self.text_widget.pack(expand=True, fill='both')

        self.label_queue = ttk.Label(self.frame_controls, text="Queue")
        self.label_queue.pack(fill='x')

        self.queue_msg = tk.Text(self.frame_controls, wrap='word', height=14, bg=LOG_BG, fg=FG_COLOR)
        self.queue_msg.pack(fill='x')

        self.label_token = ttk.Label(self.frame_controls, text="Enviar para")
        self.label_token.pack(fill='x')

        self.input_send_message = ttk.Entry(self.frame_controls)
        self.input_send_message.pack(fill='x')

        self.label_message = ttk.Label(self.frame_controls, text="Mensagem")
        self.label_message.pack(fill='x')

        self.input_message = ttk.Entry(self.frame_controls)
        self.input_message.pack(fill='x')

        self.button_send = ttk.Button(self.frame_controls, text="Enviar", command=self.send_button_clicked)
        self.button_send.pack(fill='x')

        self.corrupt_message_var = tk.BooleanVar(value=False, name="Var")
        self.checkbox_corrupt_message = ttk.Checkbutton(
            self.frame_controls, 
            text="Corromper mensagem", 
            variable=self.corrupt_message_var, 
            style='TCheckbutton',
        )
        self.checkbox_corrupt_message.setvar("Var", True)
        self.checkbox_corrupt_message.pack(fill='x')


        self.block_token_var = tk.BooleanVar(value=False, name="VarBlock")
        self.checkbox_block_token = ttk.Checkbutton(
            self.frame_controls, 
            text="Bloquear token", 
            variable=self.block_token_var, 
            style='TCheckbutton',
        )
        self.checkbox_block_token.setvar("VarBlock", True)
        self.checkbox_block_token.pack(fill='x')

        self.button_send_token = ttk.Button(self.frame_controls, text="Enviar token", command=self.send_token_next)
        self.button_send_token.pack(fill='x')

        self.label_token_status = ttk.Label(self.frame_controls, text="Token Holder: False")
        self.label_token_status.pack(fill='x')

        self.label_token_manager = ttk.Label(self.frame_controls, text="Token: --")
        self.label_token_manager.pack(fill='x')

        self.label_token_manager_timeout = ttk.Label(self.frame_controls, text="Timeout: --")
        self.label_token_manager_timeout.pack(fill='x')

        self.label_token_manager_multi = ttk.Label(self.frame_controls, text="Multi tokens: --")
        self.label_token_manager_multi.pack(fill='x')
    
   


    def send_button_clicked(self):
        destination = self.input_send_message.get()  
        message = self.input_message.get() 
        if destination and message:
            self.root.event_generate("<<SendMessage>>", when="tail") 

    def send_token_next(self):
        self.root.event_generate("<<SendToken>>", when="tail")

    def update_status(self, message, temp_instance):
        split_message = message.split(' ')
        if(split_message[0] == 'Timeout:'):
            self.label_token_manager_timeout.config(text=message)
        elif(split_message[0] == 'Multiple'):
            self.label_token_manager_multi.config(text=message)
        else:
            self.label_token_manager.config(text=message)
    def update_token_holder(self, message, temp_instance):
        self.label_token_status.config(text=message)
    def update_queue_add_first(self, message):
        message = f'{message}\n'
        self.queue_msg.insert(1.0, message)
        self.queue_msg.see(END)
    def update_queue(self, message):
        message = f'{message}\n'
        self.queue_msg.insert(END, message)
        self.queue_msg.see(END)
    def update_queue_remove_first(self):
        self.queue_msg.delete(1.0, 2.0)
    def update_logs(self, message):
        message = f'{message}\n'
        self.text_widget.insert(END, message)
        self.text_widget.see(END)

    def refresh_display(self):
        pass

class TokenRing:
    def __init__(self, display_manager):
        self.display_manager = display_manager
        self.__UDPSocket = UDPSocket(5000)
        threading.Thread(target=self.__receive_data).start()
        self.__configure()
        display_manager.root.bind("<<SendMessage>>", self.send_message_event)
        display_manager.root.bind("<<SendToken>>", self.send_token_next)
        self.__queue = queue.Queue()
        self.__temp_token_management_timeout = Temp(10, alignment=0, text='Timeout: ', update_callback=self.display_manager.update_status)
        self.__temp_token_management_multiple_tokens = Temp(5, alignment=0, text='Multiple tokens: ', update_callback=self.display_manager.update_status)
        self.__temp_with_token = Temp(self.__token_time, alignment=0, text='Token: ', update_callback=self.display_manager.update_status)
        self.__token_holder_flag = False
        self.__ack_event_thread = None
        self.__ack_event = threading.Event()
        self.__last_message = None
        if (self.__token):
            self.__temp_with_token.start(self.__send_token)

    def start(self):
        threading.Thread(target=self.__receive_data).start()
    def send_message_event(self, event=None):
        destination = self.display_manager.input_send_message.get()
        message = self.display_manager.input_message.get()
        if destination and message:
            self.send_message(message, destination)
            self.display_manager.input_send_message.delete(0, tk.END)
            self.display_manager.input_message.delete(0, tk.END) 
    
    def send_token_next(self, event=None):
        self.__send_token()

    def __receive_data(self):
        while True:
            data = self.__UDPSocket.recv()
            self.display_manager.update_logs(f'Received data {data}')
            if data:
                self.__decode_data(data.decode("utf-8"))
            else:
                self.display_manager.update_logs('No data received')
    
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
            self.display_manager.update_logs('Token removed')

        def token_timeout():
            self.display_manager.update_logs('Token timeout')
            self.__send_token()

        def multiple_tokens():
            remove_token()
        
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
        else:
            msg = data.split(':')
            msg = msg[1].split(';')
            ack = msg[0]
            origin = msg[1]
            destination = msg[2]
            crc = msg[3]
            msg_content = msg[4]
            if (destination.lower() == 'todos'):
                self.display_manager.update_logs(f'Message received {msg}')
                self.__send(data.encode('utf-8'))
            elif (origin == self.__my_nickname):
                if (ack.lower() == 'nack'):
                    print("entrei")
                    self.__ack_event.set()
                    self.display_manager.update_logs(f'Message not acknowledged {msg}')
                    print(self.__last_message)
                    self.__enqueue_message_first(self.__last_message)
                    
                elif (ack.lower() =='naoexiste'):
                    self.__ack_event.set()
                    self.display_manager.update_logs(f'Destination unreachable {msg}')
                elif (ack.lower() == 'ack'):
                    self.__ack_event.set()
                    self.display_manager.update_logs(f'Message Acknowledged {msg}')
            elif(destination == self.__my_nickname):
                if(self.__check_crc(msg_content, int(crc))):
                    self.display_manager.update_logs(f'Message received {msg}')
                    self.__send('7777:ACK;{};{};{};{}'.format(origin, destination, crc, msg_content).encode('utf-8'))
                else:
                    self.display_manager.update_logs(f'Message corrupted {msg}')
                    self.__send('7777:NACK;{};{};{};{}'.format(origin, destination, crc, msg_content).encode('utf-8'))
            else:
                self.display_manager.update_logs(f'Message not for me {msg}')
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
        # self.__last_message = None
        self.__ack_event.clear()

    @property
    def __is_token_holder(self):
        return self.__token_holder_flag

    @__is_token_holder.setter
    def __is_token_holder(self, value):
        self.display_manager.update_token_holder('Token Holder: {}'.format(value), self.__temp_token_management_timeout)
        if value and not self.__token_holder_flag: 
            self.display_manager.update_logs('Token holder')
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
        if not self.__queue.empty():
            self.display_manager.update_logs('Sending message')
            self.__send(self.__dequeue_message())
            self.__temp_with_token.start(self.__send_token)
            self.__wait_for_acknowledgement()
        else: 
            self.display_manager.update_logs('No message to send')
            self.__temp_with_token.start(self.__send_token)

    def __send_token(self):
        self.__is_token_holder = False
        if (self.__token):
            self.__temp_token_management_timeout.start(callback=self.__send_token)
            self.__temp_token_management_multiple_tokens.start()
        if(self.display_manager.checkbox_block_token.getvar("VarBlock")=="0"):
            self.__send(b'9000')

    def __enqueue_message(self, message):
        self.__queue.put(message)
        self.display_manager.update_queue(message)
    def __enqueue_message_first(self, message):
        temp_queue = queue.Queue()
        temp_queue.put(message)
        while not self.__queue.empty():
            temp_queue.put(self.__queue.get())
        self.__queue = temp_queue
        self.display_manager.update_queue_add_first(message)

    def __dequeue_message(self):
        self.display_manager.update_queue_remove_first()
        data = self.__queue.get()
        self.__last_message = data
        msg = data.decode("utf-8").split(':')
        msg = msg[1].split(';')
        origin = msg[1]
        destination = msg[2]
        crc = msg[3]
        msg_content = msg[4]
        msg_content= self.introduce_error(msg_content)
        data = '7777:naoexiste;{};{};{};{}'.format(origin, destination, crc, msg_content).encode('utf-8')
        return data
    
    def __send(self, data):
        self.display_manager.update_logs(f'Sending data {data}')
        self.__UDPSocket.send(data, (self.__right_ip, self.__right_port))

    def send_message(self, message, nickname = 'TODOS'):
        message_send = message
        msg = '7777:naoexiste;{};{};{};{}'.format(self.__my_nickname, nickname, self.__calculate_crc(message), message_send)
        self.__enqueue_message(msg.encode('utf-8'))

    def introduce_error(self, message, error_count=1):
        probability = 0.15
        if (random.random() > probability) and (self.display_manager.checkbox_corrupt_message.getvar("Var")=="0"):
            return message
        else:
            self.display_manager.update_logs(f'Corrupting message {message}')
            corrupted_bytes = bytearray(message, 'utf-8')
            message_length = len(corrupted_bytes)
            
            indices_to_corrupt = random.sample(range(message_length), error_count)
            
            for i in indices_to_corrupt:
                bit_to_flip = random.randint(0, 7)
                corrupted_bytes[i] ^= (1 << bit_to_flip)
            
            try:
                return corrupted_bytes.decode('utf-8')
            except UnicodeDecodeError:
                return corrupted_bytes.decode('utf-8', errors='replace')


def main():
    display_manager = DisplayManager()
    token_ring = TokenRing(display_manager)

    token_ring_thread = threading.Thread(target=token_ring.start)
    token_ring_thread.daemon = True

    token_ring_thread.start()
    display_manager.start_gui_loop()

    token_ring_thread.join()

if __name__ == "__main__":
    main()
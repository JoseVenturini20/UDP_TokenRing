from threading import Thread
import time
import tkinter as tk
from tkinter import ttk
import threading
from tkinter import Tk, Text, Scrollbar, END, VERTICAL
from token_ring import TokenRing 

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

BG_COLOR = "#333333"
FG_COLOR = "#CCCCCC"
LOG_BG = "#222222"
BUTTON_BG = "#555555"

style = ttk.Style()
style.configure('TLabel', background=BG_COLOR, foreground=FG_COLOR)
style.configure('TEntry', background=BG_COLOR, foreground=FG_COLOR)
style.configure('TButton', background=BUTTON_BG, foreground=FG_COLOR)
style.configure('TFrame', background=BG_COLOR)

root = tk.Tk()
root.title("Token Ring")
root.geometry('1200x450') 
root.configure(bg=BG_COLOR)

frame_logs = ttk.Frame(root, padding="3")
frame_logs.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

frame_controls = ttk.Frame(root, padding="3")
frame_controls.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
root.grid_columnconfigure(1, weight=0)

text_widget_label = ttk.Label(frame_logs, text="Logs")
text_widget_label.pack(fill='x')

text_widget = tk.Text(frame_logs, wrap='word', bg=LOG_BG, fg=FG_COLOR)
text_widget.pack(expand=True, fill='both')

label_queue = ttk.Label(frame_controls, text="Queue")
label_queue.pack(fill='x')

queue_msg = tk.Text(frame_controls, wrap='word', height=18, bg=LOG_BG, fg=FG_COLOR)
queue_msg.pack(fill='x')

label_token = ttk.Label(frame_controls, text="Enviar para")
label_token.pack(fill='x')

input_send_message = ttk.Entry(frame_controls)
input_send_message.pack(fill='x')

label_message = ttk.Label(frame_controls, text="Mensagem")
label_message.pack(fill='x')

input_message = ttk.Entry(frame_controls)
input_message.pack(fill='x')

label_token_status = ttk.Label(frame_controls, text="Token Holder: False")
label_token_status.pack(fill='x')

label_token_manager = ttk.Label(frame_controls, text="Token timer")
label_token_manager.pack(fill='x')

label_token_manager_timeout = ttk.Label(frame_controls, text="Token timeout")
label_token_manager_timeout.pack(fill='x')

label_token_manager_multi = ttk.Label(frame_controls, text="Token multi tokens")
label_token_manager_multi.pack(fill='x')

multi = 5
timeout = 10

names_list = [
    "John",
    "Mary",
    "Steven",
    "Michael",
]

def escreve():
    global multi, timeout
    for a in range(1, 50):
        text_widget.config(state=tk.NORMAL)
        if (a % 2 == 0):
            label_token_status.config(text="Token Holder: True")
        else: 
            label_token_status.config(text="Token Holder: False") 


        if (a % 10 == 0):
            queue_msg.insert(tk.END, f"7777:naoexiste;{names_list[a % 4]};{names_list[(a + 1) % 4]};12345;oiii\n")
        text_widget.insert(tk.END, f"Log exemplo {a}\n")
        text_widget.see(tk.END)  
        root.update_idletasks()  
        text_widget.config(state=tk.DISABLED)
        label_token_manager_timeout.config(text=f"Token timeout: {timeout}")
        label_token_manager_multi.config(text=f"Token multi tokens: {multi}")

        timeout-=0.5
        multi-=0.5
        if (timeout < 0):
            timeout = 10
        if (multi < 0):
            multi = 5
        time.sleep(0.5)

Thread(target=escreve).start()

root.mainloop()
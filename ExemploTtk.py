from threading import Thread
import time
import tkinter as tk

root = tk.Tk()
root.title("Mini Word")


label_token = tk.Label(root, text="Token Holder: False")
label_token.grid(row=0, column=1, sticky="nsew")

text_widget_label = tk.Label(root, text="Logs")
text_widget_label.grid(row=1, column=0, sticky="nsew")

text_widget = tk.Text(root, wrap='word')
text_widget.grid(row=2, column=0, sticky="nsew") 


label_token_manager = tk.Label(root, text="Token Manager timer")
label_token_manager.grid(row=3, column=2, sticky="nsew")

label_token_manager_timeout = tk.Label(root, text="Token timeout")
label_token_manager_timeout.grid(row=4, column=1, sticky="nsew")

label_queue = tk.Label(root, text="Queue")
label_queue.grid(row=1, column=4, sticky="nsew")

queue_msg = tk.Text(root, wrap='word')
queue_msg.grid(row=2, column=4, sticky="nsew")


label_token_manager_multi = tk.Label(root, text="Token multi tokens")
label_token_manager_multi.grid(row=4, column=3, sticky="nsew")


root.grid_columnconfigure(0, weight=1)  
root.grid_columnconfigure(1, weight=0) 
root.grid_rowconfigure(0, weight=1)

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
            label_token.config(text="Token Holder: True")
        else: 
            label_token.config(text="Token Holder: False")

        if (a % 10 == 0):
            #msg = '7777:naoexiste;{};{};{};{}'.format(self.__my_nickname, nickname, self.__calculate_crc(message), message)
            queue_msg.insert(tk.END, f"7777:naoexiste;{names_list[a % 4]};{names_list[(a + 1) % 4]};12345;oiii\n")
        text_widget.insert(tk.END, f"Log exemplo {a}\n")
        text_widget.see(tk.END)  # Scroll if necessary
        root.update_idletasks()  # Atualiza a interface gráfica
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

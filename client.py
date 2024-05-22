import socket
import select
import sys
import tkinter as tk
from threading import Thread

def send_message(event=None):
    message = entry_field.get()
    if message:
        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, "Вы: " + message + '\n')
        chat_log.config(state=tk.DISABLED)
        entry_field.delete(0, tk.END)
        try:
            s.send((message + '\n').encode())
        except Exception as e:
            chat_log.config(state=tk.NORMAL)
            chat_log.insert(tk.END, "Ошибка отправки сообщения\n")
            chat_log.config(state=tk.DISABLED)

def receive_message():
    while True:
        try:
            data = s.recv(4096)
            if not data:
                chat_log.config(state=tk.NORMAL)
                chat_log.insert(tk.END, 'ОТКЛЮЧЕНО!\n')
                chat_log.config(state=tk.DISABLED)
                s.close()
                root.quit()
                break
            else:
                chat_log.config(state=tk.NORMAL)
                chat_log.insert(tk.END, data.decode() + '\n')
                chat_log.config(state=tk.DISABLED)
        except:
            continue

if __name__ == "__main__":
    if len(sys.argv) < 2:
        host = input("Введите IP-адрес хоста: ")
    else:
        host = sys.argv[1]

    port = 5001
    name = input("СОЗДАНИЕ НОВОГО ИДЕНТИФИКАТОРА:\nВведите имя пользователя: ")
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    
    try:
        s.connect((host, port))
    except Exception as e:
        print("Не удалось подключиться к серверу:", e)
        sys.exit()

    s.send((name + '\n').encode())

    root = tk.Tk()
    root.title("Чат")

    chat_log = tk.Text(root, state=tk.DISABLED, width=50, height=20, bg="white", fg="black", wrap=tk.WORD)
    chat_log.pack(padx=10, pady=10)

    entry_frame = tk.Frame(root)
    entry_frame.pack(pady=5)

    entry_field = tk.Entry(entry_frame, width=40)
    entry_field.pack(side=tk.LEFT, padx=5)
    entry_field.bind("<Return>", send_message)

    send_button = tk.Button(entry_frame, text="Отправить", command=send_message)
    send_button.pack(side=tk.LEFT)

    receive_thread = Thread(target=receive_message)
    receive_thread.daemon = True
    receive_thread.start()

    root.mainloop()

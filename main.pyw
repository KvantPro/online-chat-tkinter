import hashlib
import json
import socket
import sys
import threading
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import *

from cryptography.fernet import Fernet

def get_ip() -> str:
    return "127.0.0.1"

class Encryptor:
	def encrypt(self, text: bytes, key: str) -> str:
		password = hashlib.sha256(key.encode())
		f = Fernet(f'{password.hexdigest()[0:43]}=')
		encrypted_text = f.encrypt(text)
		return encrypted_text.decode()

	def decrypt(self, text: str, key: str) -> bytes:
		password = hashlib.sha256(key.encode())
		f = Fernet(f'{password.hexdigest()[0:43]}=')
		encrypted_text = f.decrypt(text.encode())
		return encrypted_text

encr = Encryptor()

class Socket:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock = self.client.connect((host, port))
        except:
            showerror("Error", "Couldn't connect to server")
            sys.exit()

    def get(self, key):
        self.client.send(key.encode())
        return json.loads(self.client.recv(1024).decode().replace("'", '"'))[0]

    def listen(self, s):
        self.client.send(str(['send', encr.encrypt(b'Connect', s.pwd)]).encode())
        try:
            while True:
                self.temp = self.client.recv(1024).decode('utf-8')
                self.msgs = s.text.get(1.0, tk.END)
                s.text.delete(1.0, tk.END)
                if self.temp == 'Disconnect':
                    break
                else:
                    self.data = json.loads(self.temp.replace("'", '"'))
                    self.msgs = f"{self.msgs}{self.data[0]}: {encr.decrypt(self.data[1], s.pwd).decode()}"
                    s.text.insert(1.0, self.msgs)
        except:
            s.chat.destroy()
            s.create_menu()
    def send(self, msg, pwd):
        self.client.send(str(['send', encr.encrypt(msg.encode(), pwd)]).encode())

class Menu(tk.Tk):
    def __init__(self, master=None):
        tk.Tk.__init__(self, master)
        self.title("Онлайн чат")
        self.resizable(False, False)
        self.geometry("400x500")

        self.create_menu()
    def create_chat(self):
        self.chat = tk.Frame(width=400, height=500)

        self.label4 = ttk.Label(master=self.chat, text=f'Имя: {self.login}, Комната: {self.room}')
        self.text = tk.Text(master=self.chat, width=32, height=15)
        self.entr4 = ttk.Entry(master=self.chat)
        self.btn2 = ttk.Button(master=self.chat, text='Отправить', command=self.send)
        self.btn3 = ttk.Button(master=self.chat, text='Назад', command=self.disconnect)
        self.btn4 = ttk.Button(master=self.chat, text='Выход', command=self.exitt)

        self.label4.place(x = 30, y = 10)
        self.text.place(x = 30, y = 50)
        self.entr4.place(x = 30, y = 380, width = 240)
        self.btn2.place(x = 280, y = 380)
        self.btn3.place(x = 30, y = 420)
        self.btn4.place(x = 160, y = 420)

        self.chat.place(x = 0, y = 0)

    def create_menu(self):
        self.menu = tk.Frame(width=400, height=500)

        self.label1 = ttk.Label(master=self.menu, text='Имя: ')
        self.entr1 = ttk.Entry(master=self.menu)
        self.label2 = ttk.Label(master=self.menu, text='Комната: ')
        self.entr2 = ttk.Entry(master=self.menu)
        self.label3 = ttk.Label(master=self.menu, text='Пароль: ')
        self.entr3 = ttk.Entry(master=self.menu, show='*')
        self.var = tk.IntVar(master=self.menu)
        self.var.set(0)
        self.create = tk.Radiobutton(master=self.menu, text='Создать', variable=self.var, value=0)
        self.connect = tk.Radiobutton(master=self.menu, text='Подключится', variable=self.var, value=1)
        self.btn1 = ttk.Button(master=self.menu, text='Начать', command=self.start)
        self.exittt = ttk.Button(master=self.menu, text='Выход', command=self.exitt)

        self.label1.place(x = 30, y = 30)
        self.entr1.place(x = 120, y = 30)
        self.label2.place(x = 30, y = 70)
        self.entr2.place(x = 120, y = 70)
        self.label3.place(x = 30, y = 110)
        self.entr3.place(x = 120, y = 110)
        self.create.place(x = 30, y = 160)
        self.connect.place(x = 160, y = 160)
        self.btn1.place(x = 30, y = 210)
        self.exittt.place(x = 150, y = 210)

        self.menu.place(x = 0, y = 0)

    def send(self):
        chat.send(self.entr4.get(), self.pwd)

    def start(self):
        if self.var.get() == 0:
            a = chat.get(str(["create", self.entr1.get(), self.entr2.get(), self.entr3.get()]))
        else:
            a = chat.get(str(["connect", self.entr1.get(), self.entr2.get(), self.entr3.get()]))
        if a == 'NC':
            showerror('Error', 'Комната с таким именем уже сущетсвует')
            return
        elif a == 'ER':
            showerror('Error', 'Ошибка в комнате или пароле')
            return
        self.login = self.entr1.get()
        self.room = self.entr2.get()
        self.pwd = self.entr3.get()
        self.menu.destroy()
        t = threading.Thread(target=chat.listen, args=(self, ))
        t.start()
        self.create_chat()


    def disconnect(self):
        self.chat.destroy()
        chat.client.send(str(['send', encr.encrypt(b'Disconnect', self.pwd)]).encode())
        chat.client.send(str(['disconnect']).encode())
        self.create_menu()

    def exitt(self):
        self.destroy()

if __name__ == "__main__":
    chat = Socket(get_ip(), 2000)
    ui = Menu()
    ui.mainloop()
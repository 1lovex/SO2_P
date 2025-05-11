import socket
import tkinter as tk
from tkinter import messagebox
import threading
from datetime import datetime

HOST = 'localhost'
PORT = 12345

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Czat")
        
        self.create_login_window()
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((HOST, PORT))
        except:
            messagebox.showerror("Błąd", "Nie można połączyć z serwerem.")
            master.destroy()
            return
        
        self.username = None

    def create_login_window(self):
        self.login_window = tk.Toplevel(self.master)
        self.login_window.title("Logowanie")
        self.login_window.geometry("300x150")
        self.login_window.grab_set()

        tk.Label(self.login_window, text="Login:").pack()
        self.login_entry = tk.Entry(self.login_window)
        self.login_entry.pack()

        tk.Label(self.login_window, text="Hasło:").pack()
        self.pass_entry = tk.Entry(self.login_window, show="*")
        self.pass_entry.pack()

        tk.Button(self.login_window, text="Zaloguj", command=self.try_login).pack(pady=10)

    def try_login(self):
        login = self.login_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not login or not password:
            return

        try:
            self.socket.recv(1024)  # "Login:"
            self.socket.sendall((login + "\n").encode())

            self.socket.recv(1024)  # "Hasło:"
            self.socket.sendall((password + "\n").encode())

            response = self.socket.recv(1024).decode()

            if "Zalogowano" in response or "Zarejestrowano" in response:
                self.username = login
                self.login_window.destroy()
                # self.create_chat_ui() - TODO
                # threading.Thread(target=self.receive_messages, daemon=True).start()
            else:
                messagebox.showerror("Błąd logowania", response)
        except Exception as e:
            messagebox.showerror("Błąd", f"Coś poszło nie tak:\n{e}")
            self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
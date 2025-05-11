import socket
import tkinter as tk
from tkinter import messagebox

HOST = 'localhost'
PORT = 12345

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Czat")
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((HOST, PORT))
        except:
            messagebox.showerror("Błąd", "Nie można połączyć z serwerem.")
            master.destroy()
            return
        
        self.username = None

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
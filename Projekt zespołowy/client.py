import socket
import tkinter as tk
from tkinter import messagebox
import threading
from datetime import datetime
import re

HOST = 'localhost'
PORT = 12345

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Czat")
        
        self.bg_color = "#FFFFFF"
        self.msg_area_bg = "#EFEEF4"
        self.sent_msg_bg = "#DCF8C6"  # Zielony jak na whatsapp
        self.received_msg_bg = "#FFFFFF"
        self.header_bg = "#0088CC"    # Niebieski jak Telegram
        self.text_color = "#000000"
        self.secondary_text = "#888888"

        self.master.geometry("600x800")
        
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
                self.create_chat_ui()
                threading.Thread(target=self.receive_messages, daemon=True).start()
            else:
                messagebox.showerror("Błąd logowania", response)
        except Exception as e:
            messagebox.showerror("Błąd", f"Coś poszło nie tak:\n{e}")
            self.master.destroy()

    def create_chat_ui(self):
        self.master.configure(bg=self.bg_color)
        
        # Header z informacjami o pokoju
        header = tk.Frame(self.master, bg=self.header_bg, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="Chat Room", bg=self.header_bg, fg="white", 
                 font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=20)
        
        status_label = tk.Label(header, text=f"Zalogowany jako: {self.username}", 
                                bg=self.header_bg, fg="white", font=("Arial", 10))
        status_label.pack(side=tk.RIGHT, padx=20)

        # Canvas z scrollbarem
        chat_frame = tk.Frame(self.master, bg=self.msg_area_bg)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(chat_frame, bg=self.msg_area_bg, highlightthickness=0)
        scrollbar = tk.Scrollbar(chat_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.chat_area = tk.Frame(canvas, bg=self.msg_area_bg)

        self.chat_area.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.chat_area, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Pole do wpisywania wiadomości
        input_frame = tk.Frame(self.master, bg=self.bg_color, height=60)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        input_frame.pack_propagate(False)

        self.msg_entry = tk.Entry(input_frame, bg="white", fg=self.text_color, font=("Arial", 12))
        self.msg_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        send_button = tk.Button(input_frame, text="Wyślij", bg=self.header_bg, fg="white", 
                                 font=("Arial", 12), command=self.send_message)
        send_button.pack(side=tk.RIGHT)

    def send_message(self, event=None):
        msg = self.msg_entry.get().strip()
        if not msg:
            return

        czas = datetime.now().strftime("%H:%M")
        self.append_message(msg, sender="me", time=czas)

        try:
            self.socket.sendall(msg.encode())
        except:
            self.append_message("Błąd wysyłania wiadomości.", sender="system")
        self.msg_entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                message = self.socket.recv(1024).decode().strip()
                if message:
                    # Regex do parsowania: [HH:MM:SS] username: message
                    match = re.match(r'\[(\d{2}:\d{2}:\d{2})\] (.+?): (.+)', message)
                    if match:
                        time_str, username, msg_text = match.groups()
                        time_display = time_str[:5]  # tylko HH:MM
                        if username != self.username:
                            self.append_message(msg_text, sender="other", 
                                            time=time_display, username=username)
                    else:
                        # Wszystko co nie pasuje do formatu - traktuje jako system
                        self.append_message(message, sender="system")
            except:
                self.append_message("🔌 Rozłączono z serwerem.", sender="system")
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
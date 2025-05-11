import socket
import threading
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, messagebox
import re

HOST = 'localhost'
PORT = 12345

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("💬 Czat")
        self.master.geometry("600x800")
        
        # kolory (telegramowe)
        self.bg_color = "#FFFFFF"
        self.msg_area_bg = "#EFEEF4"
        self.sent_msg_bg = "#DCF8C6"  # Zielony jak na whatsapp
        self.received_msg_bg = "#FFFFFF"
        self.header_bg = "#0088CC"    # Niebieski jak Telegram
        self.text_color = "#000000"
        self.secondary_text = "#888888"
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((HOST, PORT))
        except:
            messagebox.showerror("Błąd", "Nie można połączyć z serwerem.")
            master.destroy()
            return

        self.username = None
        self.create_login_window()

    def create_login_window(self):
        self.login_window = tk.Toplevel(self.master)
        self.login_window.title("Logowanie")
        self.login_window.geometry("400x300")
        self.login_window.configure(bg=self.bg_color)
        self.login_window.grab_set()
        
        # Header
        header = tk.Frame(self.login_window, bg=self.header_bg, height=50)
        header.pack(fill=tk.X)
        tk.Label(header, text="💬 Zaloguj się", bg=self.header_bg, fg="white", 
                font=("Arial", 16, "bold")).pack(pady=15)

        # Login form
        form_frame = tk.Frame(self.login_window, bg=self.bg_color)
        form_frame.pack(pady=40, padx=30, fill=tk.BOTH, expand=True)
        
        tk.Label(form_frame, text="Login:", bg=self.bg_color, fg=self.text_color,
                font=("Arial", 12)).pack(anchor="w", pady=(0, 5))
        self.login_entry = tk.Entry(form_frame, font=("Arial", 12), relief="flat", 
                                   bd=1, highlightthickness=1, highlightcolor=self.header_bg)
        self.login_entry.pack(fill=tk.X, pady=(0, 20), ipady=8)

        tk.Label(form_frame, text="Hasło:", bg=self.bg_color, fg=self.text_color,
                font=("Arial", 12)).pack(anchor="w", pady=(0, 5))
        self.pass_entry = tk.Entry(form_frame, show="*", font=("Arial", 12), relief="flat",
                                  bd=1, highlightthickness=1, highlightcolor=self.header_bg)
        self.pass_entry.pack(fill=tk.X, pady=(0, 30), ipady=8)

        login_btn = tk.Button(form_frame, text="Zaloguj", command=self.try_login,
                             bg=self.header_bg, fg="white", font=("Arial", 12, "bold"),
                             relief="flat", cursor="hand2")
        login_btn.pack(fill=tk.X, ipady=10)
        
        # Enter key binding
        self.pass_entry.bind("<Return>", lambda e: self.try_login())

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
        
        tk.Label(header, text="💬 Chat Room", bg=self.header_bg, fg="white", 
                font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=20)
        
        status_label = tk.Label(header, text=f"Zalogowany jako: {self.username}", 
                               bg=self.header_bg, fg="white", font=("Arial", 10))
        status_label.pack(side=tk.RIGHT, padx=20)

        # Obszar wiadomości
        self.text_area = tk.Frame(self.master, bg=self.msg_area_bg)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas z scrollbarem dla wiadomości
        self.canvas = tk.Canvas(self.text_area, bg=self.msg_area_bg, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.text_area, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Frame wewnątrz canvas
        self.messages_frame = tk.Frame(self.canvas, bg=self.msg_area_bg)
        self.canvas_window = self.canvas.create_window((0, 0), anchor="nw", window=self.messages_frame)
        
        # Bind resize
        self.messages_frame.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        # Obszar wprowadzania wiadomości
        input_frame = tk.Frame(self.master, bg=self.bg_color)
        input_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Stylowy input
        self.msg_entry = tk.Entry(input_frame, font=("Arial", 12), relief="flat",
                                 bd=0, bg="#F5F5F5", highlightthickness=1,
                                 highlightcolor=self.header_bg)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 10))
        self.msg_entry.bind("<Return>", self.send_message)
        self.msg_entry.focus()

        # Nowoczesny przycisk wyślij
        self.send_button = tk.Button(input_frame, text="➤", command=self.send_message,
                                    bg=self.header_bg, fg="white", font=("Arial", 16),
                                    relief="flat", width=3, cursor="hand2")
        self.send_button.pack(side=tk.RIGHT)

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

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

    def append_message(self, msg, sender="system", time="", username=""):
        message_frame = tk.Frame(self.messages_frame, bg=self.msg_area_bg)
        message_frame.pack(fill=tk.X, pady=5, padx=10)
        
        if sender == "me":
            # Własne wiadomości (po prawej)
            bubble = tk.Frame(message_frame, bg=self.sent_msg_bg, relief="flat", bd=0)
            bubble.pack(side=tk.RIGHT, padx=(100, 0))
            
        elif sender == "other":
            # Wiadomości innych (po lewej)
            bubble = tk.Frame(message_frame, bg=self.received_msg_bg, relief="flat", bd=0)
            bubble.pack(side=tk.LEFT, padx=(0, 100))
            
            # Username i czas
            if username:
                username_label = tk.Label(bubble, text=username, bg=self.received_msg_bg,
                                        fg=self.header_bg, font=("Arial", 9, "bold"))
                username_label.pack(anchor="w", padx=10, pady=(8, 0))
                
        else:
            # Wiadomości systemowe (środek)
            bubble = tk.Frame(message_frame, bg=self.msg_area_bg)
            bubble.pack(anchor="center")
            
        # Tekst wiadomości
        if sender != "system":
            msg_label = tk.Label(bubble, text=msg, bg=bubble.cget('bg'), fg=self.text_color,
                               font=("Arial", 11), wraplength=300, justify="left")
            msg_label.pack(anchor="w", padx=10, pady=(0 if sender == "other" and username else 8))
            
            # Czas
            if time:
                time_label = tk.Label(bubble, text=time, bg=bubble.cget('bg'),
                                    fg=self.secondary_text, font=("Arial", 8))
                time_label.pack(anchor="e", padx=10, pady=(0, 8))
        else:
            # System message
            msg_label = tk.Label(bubble, text=msg, bg=self.msg_area_bg, fg=self.secondary_text,
                               font=("Arial", 10, "italic"))
            msg_label.pack(pady=5)
            
        # Scroll do dołu
        self.master.update_idletasks()
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
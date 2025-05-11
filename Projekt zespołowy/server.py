import socket
import threading
import os
from datetime import datetime

HOST = '0.0.0.0'
PORT = 12345
users_file = "users.txt"

clients = {}  # socket: username
lock = threading.Lock()

def load_users():
    users = {}
    if os.path.exists(users_file):
        with open(users_file, "r") as f:
            for line in f:
                if ':' in line:
                    username, password = line.strip().split(':', 1)
                    users[username] = password
    return users

def save_user(username, password):
    with open(users_file, "a") as f:
        f.write(f"{username}:{password}\n")

def authenticate(client_socket):
    client_socket.sendall("Login: ".encode())
    username = client_socket.recv(1024).decode().strip()

    client_socket.sendall("Hasło: ".encode())
    password = client_socket.recv(1024).decode().strip()

    users = load_users()
    if username in users:
        if users[username] == password:
            client_socket.sendall(f"Zalogowano jako {username}\n".encode())
            return username
        else:
            client_socket.sendall("Nieprawidłowe hasło.\n".encode())
            return None
    else:
        save_user(username, password)
        client_socket.sendall(f"Zarejestrowano i zalogowano jako {username}\n".encode())
        return username

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Serwer działa na {HOST}:{PORT}")

    try:
        while True:
            client_socket, addr = server.accept()
            # threading.Thread(target=handle_client, args=(client_socket, addr)).start()
            pass  # Will add client handling next
    except KeyboardInterrupt:
        print("\nSerwer zatrzymany.")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()
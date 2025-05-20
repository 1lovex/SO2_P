import socket
import threading
import os
from datetime import datetime

HOST = '0.0.0.0'
PORT = 12345
users_file = "users.txt"

# Dictionary to store client connections: {socket: username}
clients = {}
lock = threading.Lock()

def load_users():
    """
    Load user credentials from the users file.
    
    :returns: Dictionary of {username: password} pairs
    """
    users = {}
    if os.path.exists(users_file):
        with open(users_file, "r") as f:
            for line in f:
                if ':' in line:
                    username, password = line.strip().split(':', 1)
                    users[username] = password
    return users

def save_user(username, password):
    """
    Save a new user's credentials to the users file.
    
    :param username: The username to save
    :param password: The password to save
    """
    with open(users_file, "a") as f:
        f.write(f"{username}:{password}\n")

def authenticate(client_socket):
    """
    Handle user authentication or registration process.
    
    :param client_socket: The client socket connection
    :returns: Username if authentication succeeded, None otherwise
    
    .. seealso::
        :func:`load_users` - Function to retrieve existing users
        
        :func:`save_user` - Function to register new users
    """
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

def broadcast(message, sender_socket=None):
    """
    Send a message to all connected clients except the sender.
    
    :param message: The message to broadcast
    :param sender_socket: The socket of the sender to exclude (None for system messages)
    """
    disconnected_clients = []

    with lock:
        for client in list(clients):  # Iterate over a copy
            if client != sender_socket:
                try:
                    client.sendall(message.encode())
                except:
                    disconnected_clients.append(client)

        # Clean up disconnected clients
        for client in disconnected_clients:
            try:
                client.close()
            except:
                pass
            if client in clients:
                del clients[client]

def handle_client(client_socket, addr):
    """
    Handle an individual client connection in a separate thread.
    
    :param client_socket: The client socket connection
    :param addr: The client's address information
    
    .. seealso::
        :func:`authenticate` - Function to handle user login/registration
        
        :func:`broadcast` - Function to send messages to all clients
    """
    username = None
    try:
        while not username:
            username = authenticate(client_socket)
            if not username:
                return  # Authentication failed - disconnect

        with lock:
            clients[client_socket] = username
        broadcast(f"{username} dołączył do czatu.", client_socket)

        while True:
            message = client_socket.recv(1024)
            if not message:
                break
            time_str = datetime.now().strftime("[%H:%M:%S]")
            msg = f"{time_str} {username}: {message.decode().strip()}"
            print(msg)
            broadcast(msg, client_socket)

    except (ConnectionResetError, ConnectionAbortedError):
        print(f"[i] {addr} disconnected suddenly.")
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
    finally:
        with lock:
            if client_socket in clients:
                left_user = clients[client_socket]
                del clients[client_socket]
                broadcast(f"{left_user} opuścił czat.")
        try:
            client_socket.close()
        except:
            pass

def start_server():
    """
    Start the chat server, binding to the specified host and port,
    and accepting incoming client connections.
    
    .. seealso:: :func:`handle_client` - Function to process each client connection
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server running on {HOST}:{PORT}")

    try:
        while True:
            client_socket, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()
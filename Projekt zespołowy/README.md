# Chat Application

## Project Overview

This project implements a simple client-server chat application with a GUI interface. It allows multiple users to connect to a central server, register/login, and exchange messages in a shared chat room. The implementation uses socket programming for network communication and Tkinter for the graphical user interface.

## Table of Contents

- [Chat Application](#chat-application)
  - [Project Overview](#project-overview)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Architecture](#architecture)
  - [Technical Implementation](#technical-implementation)
    - [Server Implementation](#server-implementation)
      - [Key Components:](#key-components)
    - [Client Implementation](#client-implementation)
      - [Key Components:](#key-components-1)
    - [Threading and Synchronization](#threading-and-synchronization)
      - [Server-Side Threading:](#server-side-threading)
      - [Client-Side Threading:](#client-side-threading)
    - [Communication Protocol](#communication-protocol)
  - [User Interface](#user-interface)
  - [Building and Running](#building-and-running)
    - [Requirements](#requirements)
    - [Running the Server](#running-the-server)
    - [Running the Client](#running-the-client)

## Features

- **User Authentication**: Login and registration system
- **Real-time Messaging**: Instant message delivery to all connected users
- **Modern UI**: Telegram/WhatsApp-inspired interface with message bubbles
- **Message Formatting**: Different styling for sent, received, and system messages
- **Connection Status**: Notifications for users joining and leaving the chat
- **Timestamps**: Each message displays the time it was sent
- **Multi-threading**: Handles multiple client connections simultaneously

## Architecture

The application follows a client-server architecture:

1. **Server**:

   - Manages client connections
   - Handles user authentication
   - Broadcasts messages to connected clients
   - Maintains user state information

2. **Client**:
   - Provides a GUI for user interaction
   - Manages connection to the server
   - Sends and receives messages
   - Formats and displays chat content

## Technical Implementation

### Server Implementation

**File**: `server.py`

The server component handles multiple client connections, user authentication, and message broadcasting using threading for concurrency.

#### Key Components:

1. **User Management**:

   - Stores user credentials in a text file (`users.txt`)
   - Implements functions to load users (`load_users()`) and save new users (`save_user()`)
   - Authenticates users against stored credentials or registers new users

2. **Concurrency Handling**:

   - Each client connection is handled in a separate thread via `threading.Thread()`
   - Thread-safe operations using mutex locks (`threading.Lock()`)
   - Daemon threads for automatic cleanup when the main program exits

3. **Message Broadcasting**:

   - Central `broadcast()` function distributes messages to all connected clients
   - Thread-safe client list management via mutex lock
   - Automatic cleanup of disconnected clients during broadcast attempts

4. **Socket Programming**:
   - Uses TCP sockets (`socket.SOCK_STREAM`) for reliable message delivery
   - Binds to all network interfaces (`0.0.0.0`) to accept remote connections
   - Implements blocking accept() in the main thread with client handling in separate threads

### Client Implementation

**File**: `client.py`

The client provides a graphical interface for users to interact with the chat server, handling both sending and receiving messages asynchronously.

#### Key Components:

1. **Authentication UI**:

   - Implements a modal login window using Tkinter's `Toplevel`
   - Communicates with server for credentials verification
   - Handles login success/failure with appropriate UI feedback

2. **Chat Interface**:

   - Uses Tkinter `Canvas` with a scrollbar for flexible message display
   - Implements custom message frames for different message types
   - Maintains proper layout with dynamic resizing

3. **Network Communication**:

   - Uses TCP sockets for reliable server connection
   - Implements non-blocking receive operations in a background thread
   - Event-driven message sending from the UI thread

4. **Visual Design**:
   - Custom-styled UI elements using Tkinter widgets
   - Message bubbles with different colors based on sender
   - Responsive layout adapting to window size changes

### Threading and Synchronization

#### Server-Side Threading:

1. **Main Thread**:

   - Initializes server socket and binds to port
   - Accepts incoming client connections
   - Spawns handler threads for each new connection

2. **Client Handler Threads**:

   - One thread per connected client (created via `threading.Thread()`)
   - Handles authentication, message reception, and client disconnection
   - Runs as daemon threads (`daemon=True`) for automatic cleanup

3. **Thread Synchronization**:

   - Uses a global `threading.Lock()` object to protect shared resources
   - Critical sections protected with `lock.acquire()` and `lock.release()` (via context manager `with lock:`)
   - Synchronized access to the shared clients dictionary
   - Thread-safe broadcasting of messages to all clients

4. **Resource Management**:
   - Safe client removal from shared dictionary when disconnected
   - Socket cleanup in exception handlers and finally blocks
   - Copy-based iteration of client dictionary to avoid modification during iteration

#### Client-Side Threading:

1. **Main Thread (UI Thread)**:

   - Handles the Tkinter event loop (`root.mainloop()`)
   - Manages user interface updates
   - Processes user input and sends messages

2. **Receiver Thread**:

   - Dedicated background thread for receiving messages (`threading.Thread(target=self.receive_messages)`)
   - Non-blocking message reception
   - Updates UI through thread-safe Tkinter operations
   - Runs as daemon thread to avoid blocking application exit

3. **Thread Coordination**:
   - UI updates triggered from the receiver thread use Tkinter's thread-safe methods
   - Automatic scrolling to latest messages coordinated between threads
   - Exception handling to gracefully manage network errors

### Communication Protocol

The client and server communicate using a simple text-based protocol:

1. **Authentication Flow**:

   - Server sends "Login:" prompt
   - Client responds with username
   - Server sends "Hasło:" (Password) prompt
   - Client responds with password
   - Server responds with success/failure message

2. **Message Format**:

   - Regular messages: `[HH:MM:SS] username: message`
   - System notifications: plain text messages

3. **Connection Management**:

   - Socket disconnection triggers cleanup routines
   - Server broadcasts join/leave events to all clients

4. **Password Storage**:

   - Passwords are currently stored in plaintext
   - No encryption is implemented for data transmission

5. **Input Validation**:

   - Limited validation of user inputs
   - No protection against message flooding or spam

6. **Error Handling**:
   - Basic error messages for connection issues
   - Limited protection against malformed messages

## User Interface

The client application features a modern, mobile-inspired chat interface:

1. **Login Window**:

   - Clean, simple form with username and password fields
   - Error feedback for failed authentication attempts

2. **Chat Window**:
   - Header showing room information and user status
   - Message area with different bubble styles:
     - Right-aligned green bubbles for sent messages
     - Left-aligned white bubbles for received messages
     - Centered gray text for system notifications
   - Input area with text field and send button
   - Automatic scrolling to latest messages

## Building and Running

### Requirements

- Python 3.6 or higher
- Tkinter library (usually included with Python)
- Network connectivity between server and clients

### Running the Server

1. Open a terminal/command prompt
2. Navigate to the project directory
3. Run the server:
   ```
   python server.py
   ```
4. The server will start and display a message indicating it's running

### Running the Client

1. Open a terminal/command prompt
2. Navigate to the project directory
3. Run the client:
   ```
   python client.py
   ```
4. A login window will appear
5. Enter username and password to login or register
6. After successful authentication, the chat interface will appear

**Note**: The client is configured to connect to `localhost` by default. To connect to a remote server, modify the `HOST` variable in the client code.

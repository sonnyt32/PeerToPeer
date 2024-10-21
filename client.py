import socket
import sys
import select

HEADER_LENGTH = 10
IP = 'localhost'
PORT = 1234

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Try to connect to the server
try:
    client_socket.connect((IP, PORT))
    print("Connected to the server!")
except Exception as e:
    print(f"Error connecting to server: {e}")
    sys.exit()

# Get username
while True:
    username = input("Username: ")
    if username:
        break
    print("Username cannot be empty. Please try again.")

# Encode and send username
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username.encode('utf-8'))

# Receive and print the welcome message
try:
    welcome_message_header = client_socket.recv(HEADER_LENGTH)
    if not len(welcome_message_header):
        print("Connection closed by the server.")
        sys.exit()
    welcome_message_length = int(welcome_message_header.decode("utf-8").strip())
    welcome_message = client_socket.recv(welcome_message_length).decode('utf-8')
    print(welcome_message)
except Exception as e:
    print(f"Error receiving welcome message: {e}")
    sys.exit()

# Loop to send and receive messages
while True:
    sockets_list = [sys.stdin, client_socket]

    read_sockets, _, _ = select.select(sockets_list, [], [])

    for notified_socket in read_sockets:
        if notified_socket == client_socket:
            # Receiving a message from the server
            try:
                message_header = client_socket.recv(HEADER_LENGTH)
                if not len(message_header):
                    print("Connection closed by the server.")
                    sys.exit()
                message_length = int(message_header.decode("utf-8").strip())
                message = client_socket.recv(message_length).decode('utf-8')
                print(message)
            except Exception as e:
                print(f"Error receiving message: {e}")
                sys.exit()

        else:
            # Sending a message to the server
            message = input(f"{username}: ")
            if message:
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                client_socket.send(message_header + message.encode('utf-8'))

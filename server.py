import socket
import select

HEADER_LENGTH = 10
IP = 'localhost'  # Use '127.0.0.1' for local testing
PORT = 1234

try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print(f"Server is listening on {IP}:{PORT}...")
except Exception as e:
    print(f"Error setting up server: {e}")
    exit(1)

sockets_list = [server_socket]
clients = {}

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}
    except Exception as e:
        print(f"Error receiving message: {e}")
        return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            print(f"Accepted new connection from {client_address[0]}:{client_address[1]}")

            user = receive_message(client_socket)
            if user is False:
                continue
            
            sockets_list.append(client_socket)
            clients[client_socket] = user
            print(f"Username received: {user['data'].decode('utf-8')}")

            # Send welcome message to the new client
            welcome_message = f"Welcome {user['data'].decode('utf-8')}!"
            welcome_header = f"{len(welcome_message):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(welcome_header + welcome_message.encode('utf-8'))
            print(f"Sent welcome message to {user['data'].decode('utf-8')}")

        else:
            message = receive_message(notified_socket)
            if message is False:
                print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

            # Broadcast message to all clients except the sender
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]

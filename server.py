import socket
import threading
from datetime import datetime

HOST = '127.0.0.1'
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []
chat_history = []
BAD_WORDS = ['badword1', 'badword2']  # Example filter

def clean_message(message):
    for word in BAD_WORDS:
        message = message.replace(word, '*' * len(word))
    return message

def broadcast(message, sender=None):
    timestamp = datetime.now().strftime('%H:%M:%S')
    formatted = f"[{timestamp}] {message}"
    chat_history.append(formatted)
    for client in clients:
        if client != sender:
            client.send(formatted.encode('utf-8'))

def handle(client):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            nickname = nicknames[clients.index(client)]

            if message.startswith("/"):
                if message.startswith("/list"):
                    user_list = ", ".join(nicknames)
                    client.send(f"Users online: {user_list}".encode('utf-8'))
                elif message.startswith("/quit"):
                    raise Exception("User quit")
                elif message.startswith("/pm"):
                    parts = message.split(" ", 2)
                    if len(parts) < 3:
                        client.send("Usage: /pm <user> <message>".encode('utf-8'))
                        continue
                    target_nick, pm_msg = parts[1], parts[2]
                    if target_nick in nicknames:
                        target_index = nicknames.index(target_nick)
                        target_client = clients[target_index]
                        target_client.send(f"[PM from {nickname}]: {pm_msg}".encode('utf-8'))
                    else:
                        client.send(f"User {target_nick} not found.".encode('utf-8'))
                elif message.startswith("/help"):
                    help_text = "/list - list users\n/quit - quit chat\n/pm <user> <message> - private message"
                    client.send(help_text.encode('utf-8'))
                else:
                    client.send("Unknown command. Type /help".encode('utf-8'))
            else:
                clean_msg = clean_message(message)
                broadcast(f"{nickname}: {clean_msg}", sender=client)

        except:
            if client in clients:
                index = clients.index(client)
                nickname = nicknames[index]
                clients.remove(client)
                nicknames.remove(nickname)
                client.close()
                broadcast(f"{nickname} left the chat.")
            break

def receive():
    print('Server is running and listening...')
    while True:
        try:
            client, address = server.accept()
            print(f'Connected with {str(address)}')

            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')

            nicknames.append(nickname)
            clients.append(client)

            print(f'Nickname is {nickname}')
            broadcast(f"{nickname} joined the chat!")

            client.send("Connected to the server!\nType /help for commands.".encode('utf-8'))

            # Send last 10 chat history messages
            for msg in chat_history[-10:]:
                client.send(msg.encode('utf-8'))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
        except Exception as e:
            print(f"Server error: {e}")
            break

def admin_commands():
    while True:
        command = input("")
        if command == "/shutdown":
            print("Shutting down server...")
            broadcast("Server is shutting down.")
            for client in clients:
                client.close()
            server.close()
            break

# Start server threads
threading.Thread(target=receive).start()
threading.Thread(target=admin_commands).start()

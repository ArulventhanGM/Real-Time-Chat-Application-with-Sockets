import socket
import threading

nickname = input("Choose your nickname: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 12345))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
            else:
                print(message)
        except:
            print("Disconnected from server.")
            client.close()
            break

def write():
    while True:
        try:
            message = input()
            if message.strip() == "":
                continue
            client.send(message.encode('utf-8'))
            if message == "/quit":
                client.close()
                break
        except:
            break

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

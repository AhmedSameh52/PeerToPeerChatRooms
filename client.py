import socket
import threading
import hashlib

# Connect to OS ports
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.bind(('', 0))
PORT = client.getsockname()[1] # Client Port Number (Randomized by OS)

# CONSTANTS
HEADER = 64 # Header Size
FORMAT = 'utf-8' # Message Encoding Format
DISCONNECT_MESSAGE = "!DISCONNECT" # Disconnect when this message is recieved
IPADDRESS = socket.gethostbyname(socket.gethostname())   # Get the local IP address
ADDR = (IPADDRESS, PORT)

client.connect(("192.168.100.11", 55050)) # Connect to the server

def receiveMessageFromServer():
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            print(message)
        except:
            print("An error occured!")
            client.close()
            break

def sendMessageToServer():
        # LOGIN COMMAND TEST
        username = '{}'.format(input('Username: '))
        password = '{}'.format(input('Password: '))
        password = hashlib.sha256(password.encode()).hexdigest()
        message = f'CREATE <{username}> <{password}>'
        client.send(message.encode(FORMAT))

if __name__ == "__main__":
    nickname = "nickname"

    receive_thread = threading.Thread(target=receiveMessageFromServer)
    receive_thread.start()

    write_thread = threading.Thread(target=sendMessageToServer)
    write_thread.start()



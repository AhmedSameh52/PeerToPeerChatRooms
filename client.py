import socket
import threading

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
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            print("An error occured!")
            client.close()
            break

def sendMessageToServer():
    while True:
        message = '{}: {}'.format(nickname, input(''))
        client.send(message.encode('ascii'))

if __name__ == "__main__":
    nickname = "ahmed"

    receive_thread = threading.Thread(target=receiveMessageFromServer)
    receive_thread.start()

    write_thread = threading.Thread(target=sendMessageToServer)
    write_thread.start()



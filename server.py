import threading
import socket

HOST = socket.gethostbyname(socket.gethostname())
PORT = 55050
FORMAT = 'utf-8' # Message Encoding Format

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(1024)
            broadcast(message)
        except:
            # Removing And Closing Clients
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast('{} left!'.format(nickname).encode(FORMAT))
            nicknames.remove(nickname)
            break

def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request And Store Nickname
        # client.send('LOGIN_REQUEST'.encode('ascii')) # Send Login Request to Client

        # Execute Commands according to Message Received
        messageReceived = client.recv(1024).decode(FORMAT).split(" ")
        match messageReceived[0]:
            # Send message command is not added as the server does not execute this command
            case "LOGIN":
                print("login command needs to be executed!")
            case "CREATE":
                print("signup command needs to be executed!")
            case "LOGOUT":
                print("logout command needs to be executed!")
            case "LIST_ONLINE_USERS":
                print("list online users command needs to be executed!")
            case "LIST_ONLINE_CHATROOMS":
                print("list online chatrooms command needs to be executed!")
            case "CREATE_ROOM":
                print("create room command needs to be executed!")
            case "JOIN_ROOM":
                print("join room command needs to be executed!")
            case "LEAVE_ROOM":
                print("leave room command needs to be executed!")
            case "KICK":
                print("kick command needs to be executed!")
            case "INVITE":
                print("invite command needs to be executed!")
            case "LEAVE_CHAT":
                print("leave chat command needs to be executed!")
            case "HELLO":
                print("hello command needs to be executed!")
            case _:
                print("command unknown!")

        nicknames.append(messageReceived[0])
        clients.append(client)

        # Print And Broadcast Nickname
        print("Nickname is {}".format(messageReceived[0]))
        broadcast("{} joined!".format(messageReceived[0]).encode(FORMAT))
        client.send('Connected to server!'.encode(FORMAT))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server is listening...")
receive()
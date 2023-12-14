import threading
import socket
import sqlite3
import re

HOST = socket.gethostbyname(socket.gethostname())
PORT = 55050
FORMAT = 'utf-8' # Message Encoding Format

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []

def loginCommand(messageReceived):
    #  ACCEPT 200 -> 0 /// FAILED 500 -> 1/// NOT_FOUND 401 -> 2 /// INCORRECT_PASSWORD 402 -> 3
    try:
        username = re.search(r'<(.*?)>', messageReceived[1]).group(1)
        password = re.search(r'<(.*?)>', messageReceived[2]).group(1)
        if username == "" or password == "":
            return 1
            
        conn = sqlite3.connect("networksProject.db")
        cur = conn.cursor()

        cur.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cur.fetchone()

        if result:
            stored_password = result[0]
            if stored_password == password:
                # Passwords match
                return 0
            else:
                # Passwords do not match
                return 3
        else:
            # Username not found
            return 2
    except:
        return 1

def signupCommand(messageReceived):
    # ACCEPT 200 -> 0 /// USERNAME_TAKEN 400 -> 1 /// FAILED 500 -> 2
    try:
        username = re.search(r'<(.*?)>', messageReceived[1]).group(1)
        password = re.search(r'<(.*?)>', messageReceived[2]).group(1)

        conn = sqlite3.connect("networksProject.db")
        cur = conn.cursor()

        cur.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cur.fetchone()

        if result:
            # Username already exists
            return 1
        else:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return 0
    except:
        return 2

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

        # Execute Commands according to Message Received
        messageReceived = client.recv(1024).decode(FORMAT).split(" ")
        match messageReceived[0]:
            # Send message command is not added as the server does not execute this command
            case "LOGIN":
                responseCode = loginCommand(messageReceived)
                if responseCode == 0:
                   client.send('ACCEPT 200'.encode(FORMAT))
                elif responseCode == 1:
                    client.send('FAILED 500'.encode(FORMAT))
                elif responseCode == 2:
                    client.send('NOT_FOUND 401'.encode(FORMAT))
                elif responseCode == 3:
                    client.send('INCORRECT_PASSWORD 402'.encode(FORMAT))
                
            case "CREATE":
                responseCode = signupCommand(messageReceived)
                if responseCode == 0:
                   client.send('ACCEPT 200'.encode(FORMAT))
                elif responseCode == 1:
                    client.send('USERNAME_TAKEN 400'.encode(FORMAT))
                elif responseCode == 2:
                    client.send('FAILED 500'.encode(FORMAT))
     
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
        #("Nickname is {}".format(messageReceived[0]))
        #broadcast("{} joined!".format(messageReceived[0]).encode(FORMAT))
        #client.send('Connected to server!'.encode(FORMAT))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server is listening...")
receive()
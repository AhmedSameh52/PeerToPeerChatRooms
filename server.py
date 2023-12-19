import threading
import socket
import sqlite3
import re
from user import User
import time

HOST = socket.gethostbyname(socket.gethostname())
PORT = 55050
UDPPORT = 55555
FORMAT = 'utf-8' # Message Encoding Format

peersConnected = []

def decreaseHelloTimers():
    global peersConnected
    try:
        while True:

            for i, peer in enumerate(peersConnected):
                peersConnected[i].helloTimerRemaining -= 1
                # print(f"Decreased remaining time of {peersConnected[i].username} and bacame {peersConnected[i].helloTimerRemaining}")
                if peersConnected[i].helloTimerRemaining == 0:
                    del peersConnected[i]

            time.sleep(3)
    except Exception as e:
        print(e)



def UDPHello(client_socket):
    global peersConnected
    clientUsername = None
    try:
        while True:
            data, _ = client_socket.recvfrom(1024)
            decoded_data = data.decode(FORMAT)

            if decoded_data.startswith("HELLO"):
                _, clientUsername = decoded_data.split("<")
                clientUsername = clientUsername[:-1]  # Remove ">" from the end
                indexPeersConnected = next((index for index, User in enumerate(peersConnected) if User.username == clientUsername), None)
                if indexPeersConnected is not None:
                    peersConnected[indexPeersConnected].helloTimerRemaining = peersConnected[indexPeersConnected].helloTimerRemaining + 1
                    # print(f"Increased remaining time of {clientUsername} and bacame {peersConnected[indexPeersConnected].helloTimerRemaining}")
                else:
                    break
    except:
            print(f"{clientUsername} caused an error.")


def loginCommand(messageReceived, address):
    #  ACCEPT 200 -> 0 /// FAILED 500 -> 1/// NOT_FOUND 401 -> 2 /// INCORRECT_PASSWORD 402 -> 3
    try:
        ip, port = address
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
                newUser = User(username= username, password = password, ip_address = ip, port_number = port)
                peersConnected.append(newUser)
                return 0
            else:
                # Passwords do not match
                return 3
        else:
            # Username not found
            return 2
    except:
        return 1

def signupCommand(messageReceived, address):
    # ACCEPT 200 -> 0 /// USERNAME_TAKEN 400 -> 1 /// FAILED 500 -> 2
    try:
        ip, port = address
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
            newUser = User(username= username, password = password, ip_address = ip, port_number = port)
            peersConnected.append(newUser)
            return 0
    except:
        return 2

def logoutCommand(userObject):
    # ACCEPT 200 -> 0 /// FAILED 500 -> 1
    try:
        index_to_remove = next((index for index, User in enumerate(peersConnected) if User.username == userObject.username and User.ip_address == userObject.ip_address and User.password == userObject.password and User.port_number == userObject.port_number), None)

        # Remove the user from the array if found
        if index_to_remove is not None:
            del peersConnected[index_to_remove]
            return 0
        else:
            return 1
    except:
        return 1

def listOnlineUsersCommand(client):
    try:
        peersUsername = "<"
        for peer in peersConnected:
            peersUsername = peersUsername + peer.username + ' '
        peersUsername = peersUsername[:-1] + '>' # Remove the last space and replace it with closing angle brackets
        message = "ACCEPT 200 " + peersUsername
        client.send(message.encode(FORMAT))
    except:
        client.send('FAILED 500'.encode(FORMAT))



def receive(client, address):
    # Accept Connection
    ip, port = address  # Extract IP and port from the address tuple
    userObject = None
    print(f"Connected with {ip}:{port}")
    try:
        while True:
            # Execute Commands according to Message Received
            messageReceived = client.recv(1024).decode(FORMAT).split(" ")
            match messageReceived[0]:
                # Send message command is not added as the server does not execute this command
                case "LOGIN":
                    responseCode = loginCommand(messageReceived, address)
                    if responseCode == 0:
                        userObject = next((User for User in peersConnected if User.ip_address == ip and User.port_number == port), None)
                        if userObject == None:
                            client.send('FAILED 500'.encode(FORMAT)) 
                        client.send('ACCEPT 200'.encode(FORMAT))
                    elif responseCode == 1:
                        client.send('FAILED 500'.encode(FORMAT))
                    elif responseCode == 2:
                        client.send('NOT_FOUND 401'.encode(FORMAT))
                    elif responseCode == 3:
                        client.send('INCORRECT_PASSWORD 402'.encode(FORMAT))
                    
                case "CREATE":
                    responseCode = signupCommand(messageReceived, address)
                    if responseCode == 0:
                        userObject = next((User for User in peersConnected if User.ip_address == ip and User.port_number == port), None)
                        if userObject == None:
                            client.send('FAILED 500'.encode(FORMAT)) 
                        client.send('ACCEPT 200'.encode(FORMAT))
                    elif responseCode == 1:
                        client.send('USERNAME_TAKEN 400'.encode(FORMAT))
                    elif responseCode == 2:
                        client.send('FAILED 500'.encode(FORMAT))

                case "LOGOUT":  
                    responseCode = logoutCommand(userObject)      
                    if responseCode == 0:
                        userObject = None
                        client.send('ACCEPT 200'.encode(FORMAT))
                    elif responseCode == 1:
                        client.send('FAILED 500'.encode(FORMAT))

                case "LIST_ONLINE_USERS":
                    try:
                        peersUsername = "<"
                        for peer in peersConnected:
                            peersUsername = peersUsername + peer.username + ' '
                        peersUsername = peersUsername[:-1] + '>' # Remove the last space and replace it with closing angle brackets
                        message = "ACCEPT 200 " + peersUsername
                        client.send(message.encode(FORMAT))
                    except:
                        client.send('FAILED 500'.encode(FORMAT))
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
                    print(messageReceived)

            print("\n--------------Connected Peers------------------")
            for peer in peersConnected:
                print("Username:", peer.username)
                print("Password:", peer.password)
                print("IP Address:", peer.ip_address)
                print("Port Number:", peer.port_number)
                print("--------------------------------")
    except:
        index_to_remove = next((index for index, User in enumerate(peersConnected) if User.username == userObject.username and User.ip_address == userObject.ip_address and User.password == userObject.password and User.port_number == userObject.port_number), None)
        if index_to_remove is not None:
            del peersConnected[index_to_remove]
        client.close()

def startConnectionWithClients():
    # TCP CONNECTION
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', PORT))
    server.listen()

    #UDP CONNECTION
    UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPsocket.bind(('localhost', UDPPORT))

    #Start Hello Timer
    timerThread = threading.Thread(target=decreaseHelloTimers)
    timerThread.start()
    while True:
        try:
            client, address = server.accept()
            thread = threading.Thread(target=receive, args=(client,address,))
            thread.start()
            data, client_address = UDPsocket.recvfrom(1024)
            UDPThread = threading.Thread(target=UDPHello, args = (UDPsocket,))
            UDPThread.start()
        except:
            pass

if __name__ == "__main__":
    print("Server is listening...")
    startConnectionWithClients()
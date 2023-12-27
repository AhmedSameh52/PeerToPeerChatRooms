import socket
import threading
import hashlib
import time
from formats import *
from peer import Peer
import getpass
import re



# Connect to OS ports TCP CONNECTION
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.bind(('', 0))
PORT = client.getsockname()[1] # Client Port Number (Randomized by OS)
client.connect(('localhost', 55050)) # Connect to the server

# CONSTANTS
HEADER = 64 # Header Size
FORMAT = 'utf-8' # Message Encoding Format
DISCONNECT_MESSAGE = "!DISCONNECT" # Disconnect when this message is recieved
IPADDRESS = socket.gethostbyname(socket.gethostname())   # Get the local IP address
ADDR = (IPADDRESS, PORT)

isUserLoggedIn = False
clientUsername = None
peerNodesConnected = []
lastFreePortNumber = None
lastFreeIP = None
# Connect to OS ports UDP CONNECTION
def UDPConnection():
    global clientUsername

    sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockUDP.bind(('', 0))
    try:
        while True: 
            if clientUsername is not None:
                sockUDP.sendto(f"HELLO <{clientUsername}>".encode(FORMAT), ('localhost', 55555))
                # print("message should be sent")
                time.sleep(3)
    except Exception as e: 
        sockUDP.close()
        print(e)



def receiveMessageFromServer():
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            messagesRecievedFromServer.append(message)
        except:
            print("An error occured!")
            client.close()
            break

def sendMessageToServer(message):
        # LOGIN COMMAND TEST
        username = '{}'.format(input('Username: '))
        password = '{}'.format(input('Password: '))
        password = hashlib.sha256(password.encode()).hexdigest()
        message = f'LOGIN <{username}> <{password}>'
        client.send(message.encode(FORMAT))

def sendLoginRequest():
    global isUserLoggedIn
    global clientUsername

    username = '{}'.format(input(f"{MAGENTA}Username: {YELLOW}{ITALIC}"))
    print(Style.RESET_ALL)
    password = '{}'.format(input(f"{MAGENTA}Password: {YELLOW}{ITALIC}"))
    print(Style.RESET_ALL)
    print(f"{BRIGHT}Processing....")
    print(Style.RESET_ALL)

    password = hashlib.sha256(password.encode()).hexdigest()
    message = f'LOGIN <{username}> <{password}>'
    client.send(message.encode(FORMAT))
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if message == "ACCEPT 200":
                isUserLoggedIn = True
                clientUsername = username
                print(f"{BRIGHT}{GREEN}Login Success!")
                print(Style.RESET_ALL)
                return
            elif message == "NOT_FOUND 401":
                print(f"{BRIGHT}{RED}The username does not exist in the database, please try again.")
                print(Style.RESET_ALL)
                return
            elif message == "INCORRECT_PASSWORD 402":
                print(f"{BRIGHT}{RED}Incorrect Password Entered, please try again.")
                print(Style.RESET_ALL)
                return
            elif message == "FAILED 500":
                print(f"{BRIGHT}{RED}An error has occured while logging you in, please try again.")
                print(Style.RESET_ALL)
                return
        except:
            print(f"{BRIGHT}{RED}An error occured with the connection!")
            print(Style.RESET_ALL)
            client.close()
            break

def sendSignupRequst():
    global isUserLoggedIn
    global clientUsername

    username = '{}'.format(input(f"{MAGENTA}Username: {YELLOW}{ITALIC}"))
    print(Style.RESET_ALL)
    password = '{}'.format(input(f"{MAGENTA}Password: {YELLOW}{ITALIC}"))
    print(Style.RESET_ALL)
    print(f"{BRIGHT}Processing....")
    print(Style.RESET_ALL)
    
    password = hashlib.sha256(password.encode()).hexdigest()
    message = f'CREATE <{username}> <{password}>'
    client.send(message.encode(FORMAT))
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if message == "ACCEPT 200":
                isUserLoggedIn = True
                clientUsername = username
                print(f"{BRIGHT}{GREEN}Account Created Successfully!")
                print(Style.RESET_ALL)
                return
            elif message == "USERNAME_TAKEN 400":
                print(f"{BRIGHT}{RED}The username already exists in the database, please try again.")
                print(Style.RESET_ALL)
                return
            elif message == "FAILED 500":
                print(f"{BRIGHT}{RED}An error has occured while creating an account, please try again.")
                print(Style.RESET_ALL)
                return
        except:
            print(f"{BRIGHT}{RED}An error occured with the connection!")
            print(Style.RESET_ALL)
            client.close()
            break

def sendLogoutRequst():
    global isUserLoggedIn
    global clientUsername

    message = 'LOGOUT'
    client.send(message.encode(FORMAT))
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if message == "ACCEPT 200":
                isUserLoggedIn = False
                clientUsername = None
                print(f"{BRIGHT}{GREEN}Logged Out Successfully!")
                print(Style.RESET_ALL)
                return
            elif message == "FAILED 500":
                print(f"{BRIGHT}{RED}An error has occured while logging out, please try again.")
                print(Style.RESET_ALL)
                return
        except:   
            print(f"{BRIGHT}{RED}An error occured with the connection!")
            print(Style.RESET_ALL)
            client.close()
            break

def sendListOnlineUsersRequest():
    message = 'LIST_ONLINE_USERS'
    client.send(message.encode(FORMAT))
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if "ACCEPT 200" in message:
                message = message.replace("ACCEPT 200", '')
                message = message.replace("<", '')
                message = message.replace(">", '')
                onlineUsersList = [word for word in message.split() if word] # Split the message into a list

                print(f"{BRIGHT}{GREEN}Command Executed Successfully!")
                print(Style.RESET_ALL)
                print(f"{BRIGHT}{WHITE}Online Users: ")
                for user in onlineUsersList:
                    print(f"{BRIGHT}{CYAN}{user}")
                print(Style.RESET_ALL)
                return
            elif message == "FAILED 500":
                print(f"{BRIGHT}{RED}An error has occured while executing the command, please try again.")
                print(Style.RESET_ALL)
                return
        except:
            print(f"{BRIGHT}{RED}An error occured with the connection!")
            print(Style.RESET_ALL)
            client.close()
            break

def sendResetPasswordRequst():
    global clientUsername

    password = '{}'.format(input(f"{MAGENTA}New Password: {YELLOW}{ITALIC}"))
    password = hashlib.sha256(password.encode()).hexdigest()
    print(Style.RESET_ALL)
    print(f"{BRIGHT}Processing....")
    print(Style.RESET_ALL)

    message = f"RESET_PASSWORD <{clientUsername}> <{password}>"
    client.send(message.encode(FORMAT))
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if message == "ACCEPT 200":
                print(f"{BRIGHT}{GREEN}Password Reset Successfully!")
                print(Style.RESET_ALL)
                return
            elif message == "FAILED 500":
                print(f"{BRIGHT}{RED}An error has occured while resetting the password, please try again.")
                print(Style.RESET_ALL)
                return
        except:   
            print(f"{BRIGHT}{RED}An error occured with the connection!")
            print(Style.RESET_ALL)
            client.close()
            break

def acceptPeers(peerConnection, address):
    global lastFreePortNumber
    global lastFreeIP
    ip, port = address
    while True:
        try:
            messageReceived = peerConnection.recv(1024).decode(FORMAT).split(" ")
            if messageReceived[0] == "JOIN_ROOM_REQUEST":
                peerUsername = re.search(r'<(.*?)>', messageReceived[1]).group(1)
                freePortNumber = int(re.search(r'<(.*?)>', messageReceived[2]).group(1))
                
                print(f"{BLUE}User {GREEN}{peerUsername} {BLUE}want to join your room! Type {MAGENTA}Yes{BLUE} to accept the invitation or {MAGENTA}No {BLUE}to reject it")
                print(f"{BLUE}Type !respond in the chat to respond to the message")
                print(Style.RESET_ALL)
                decision = '{}'.format(input(f"{YELLOW}{ITALIC}"))
                print(Style.RESET_ALL)
                
                if decision == "Yes" or decision == "yes" or decision == "y" or decision == "Y":
                    peerConnection.send(f"ACCEPT 200 <{lastFreeIP}> <{lastFreePortNumber}>".encode(FORMAT))
                    lastFreePortNumber = freePortNumber
                    lastFreeIP = ip
                elif decision == "No" or decision == "no" or decision == "n" or decision == "N":
                    peerConnection.send('REQUEST_DECLINED 406'.encode(FORMAT))
                    peerConnection.close()

        except:
            peerConnection.close()
        
def acceptInvitations(peerNodeServer):
    while True:
        try:
            peerConnection, address = peerNodeServer.accept()
            thread = threading.Thread(target=acceptPeers, args=(peerConnection, address, ))
            thread.start()
            
        except:
            pass

def handleChatRoomAdmin(roomName, peerNodeServer, peerNodeListen, peerPortNumberListen):
    thread = threading.Thread(target=acceptInvitations, args=(peerNodeServer,))
    thread.start()
    threadListen = threading.Thread(target=peerListen, args=(peerNodeListen,))
    threadListen.start()
    peerSend(True, roomName)


def peerSend(isAdmin, roomName):
    global peerNodesConnected
    if isAdmin:
        print(f"{BLUE}To exit the chat room type {RED}{ITALIC}!back{Style.RESET_ALL}{BLUE},the room will be deleted afterwards!{Style.RESET_ALL}")
    else:
        print(f"{BLUE}To exit the chat room type {RED}{ITALIC}!back{Style.RESET_ALL}{BLUE}{Style.RESET_ALL}")
    while True:
        message = '{}'.format(input(f"{YELLOW}{ITALIC}"))
        messageToBeSent = f"SEND_MESSAGE <{clientUsername}> <{message}>"
        if message == "!back":
            if isAdmin:
                deleteChatRoomRequest(roomName)
            # When someone leaves the room
            return 
        elif message == "!respond":
            time.sleep(5)
        for peerNode in peerNodesConnected:
            peerNode.send(messageToBeSent.encode(FORMAT))
        print(f"{Style.RESET_ALL}{YELLOW}{clientUsername}: {MAGENTA}{message}{Style.RESET_ALL}")

def peerReceive(peerNode, IPToConnect, PortNumberToConnect, connectFirst):
    global peerNodesConnected
    
    if connectFirst:
        peerNode.connect((IPToConnect, PortNumberToConnect)) # Connect to the other peer defined by admin
    
    peerNodesConnected.append(peerNode)
    while True:
            try:
                messageReceived = peerNode.recv(1024).decode(FORMAT)
                messageRecivedList = messageReceived.split(" ")
                if messageRecivedList[0] == "SEND_MESSAGE":
                    peerUsername = re.search(r'<(.*?)>', messageRecivedList[1]).group(1)
                    message = re.search(r'<(.*?)>', messageRecivedList[2]).group(1)
                    
                    for node in peerNodesConnected:
                        if node == peerNode:
                            continue
                        node.send(messageReceived.encode(FORMAT))
                    print(f"{MAGENTA}{peerUsername}: {WHITE}{message}")
                    print(Style.RESET_ALL)
            except Exception as e:
                print(e)   
                print(f"{BRIGHT}{RED}An error occured with the connection!")
                print(Style.RESET_ALL)
                peerNode.close()
                break

def peerListen(peerNodeListen):
     while True:
        try:
            peerConnection, address = peerNodeListen.accept()
            ip, port = address
            thread = threading.Thread(target=peerReceive, args=(peerConnection, ip, port, False))
            thread.start()
            
        except:
            pass
    

def handleChatRoomPeer(peerNodeAdmin, roomName, peerPortNumberListen, peerNodeListen, peerNodeSend):
    peersConnectedToRoom = []
    try:
        message = f"JOIN_ROOM_REQUEST <{clientUsername}> <{peerPortNumberListen}>"
        peerNodeAdmin.send(message.encode(FORMAT))
        while True:
            message = peerNodeAdmin.recv(1024).decode(FORMAT).split(" ")
            if message[0] == "ACCEPT" and message[1] == "200":
                print(f"{BRIGHT}{GREEN}Request to Join Accepted.")
                print(Style.RESET_ALL)
                
                IPToConnect = re.search(r'<(.*?)>', message[2]).group(1)
                PortNumberToConnect = int(re.search(r'<(.*?)>', message[3]).group(1))
                thread = threading.Thread(target=peerReceive, args=(peerNodeSend, IPToConnect, PortNumberToConnect, True))
                thread.start()
                threadListen = threading.Thread(target=peerListen, args=(peerNodeListen,))
                threadListen.start()
                peerSend(False, roomName)                 
                    
            elif message == "REQUEST_DECLINED 406":
                print(f"{BRIGHT}{RED}Request to Join Declined.")
                print(Style.RESET_ALL)
                peerNodeAdmin.close()
                return
            elif message == "FAILED 500":
                print(f"{BRIGHT}{RED}An error has occured while joining the room, please try again.")
                print(Style.RESET_ALL)
                peerNodeAdmin.close()
                return
        
    except Exception as e:
        print(e)
        print(f"{BRIGHT}{RED}An error has occured while joining the room, please try again.")
        print(Style.RESET_ALL)
        peerNodeAdmin.close()
        return
        
def sendJoinChatroomRequest():
    # 1 -> room joining successfully, 0 -> room joining failed 
    roomName = '{}'.format(input(f"{MAGENTA}Room Name: {YELLOW}{ITALIC}"))
    print(Style.RESET_ALL)
    print(f"{BRIGHT}Processing....")
    print(Style.RESET_ALL)

    message = f"JOIN_ROOM <{roomName}>"
    client.send(message.encode(FORMAT))
    while True:
        try:
            message = client.recv(1024).decode(FORMAT).split(" ")
            if "ACCEPT" in message and "200" in message:
                adminIP = re.search(r'<(.*?)>', message[2]).group(1)
                adminPortNumber = int(re.search(r'<(.*?)>', message[3]).group(1))
                return adminIP, adminPortNumber, roomName
            elif message == "FAILED 500":
                print(f"{BRIGHT}{RED}An error has occured while executing the command, please try again.")
                print(Style.RESET_ALL)
                return 0, 0, roomName
        except Exception as e:
            print(e)
            print(f"{BRIGHT}{RED}An error occured with the connection!")
            print(Style.RESET_ALL)
            client.close()
            break
    return 0, 0, roomName

def sendCreateChatroomRequest(newPortNumber):
    # 1 -> room created successfully, 0 -> room creation failed 
    roomName = '{}'.format(input(f"{MAGENTA}Room Name: {YELLOW}{ITALIC}"))
    print(Style.RESET_ALL)
    print(f"{BRIGHT}Processing....")
    print(Style.RESET_ALL)

    message = f"CREATE_ROOM <{roomName}> <{newPortNumber}>"
    client.send(message.encode(FORMAT))
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if message == "ACCEPT 200":
                print(f"{BRIGHT}{GREEN}Room Created Successfully with name {roomName}!")
                print(Style.RESET_ALL)
                return 1, roomName
            elif message == "NAME_EXISTS 403":
                print(f"{BRIGHT}{RED}Name of the room already exists, please try again.")
                print(Style.RESET_ALL)
                return 0, roomName
            elif message == "FAILED 500":
                print(f"{BRIGHT}{RED}An error has occured while creating the room, please try again.")
                print(Style.RESET_ALL)
                return 0, roomName
        except Exception as e:
            print(e)   
            print(f"{BRIGHT}{RED}An error occured with the connection!")
            print(Style.RESET_ALL)
            client.close()
            break
    return 0, roomName

def deleteChatRoomRequest(chatRoomName):
    # 1 -> room deleted successfully, 0 -> room deletion failed 
    message = f"DELETE_ROOM <{chatRoomName}>"
    client.send(message.encode(FORMAT))
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if message == "ACCEPT 200":
                return 1
            elif message == "FAILED 500":
                return 0
        except:   
            print(f"{BRIGHT}{RED}An error occured with the connection!")
            print(Style.RESET_ALL)
            client.close()
            break
    return 0




if __name__ == "__main__":
    # Start UDP Socket Thread
    helloThread = threading.Thread(target=UDPConnection)
    helloThread.start()
    print(f"{MAGENTA_BG}{BRIGHT}{ITALIC}\t\tWelcome to ASU Chatrooms!")
    print(Style.RESET_ALL)
    print(f"{BRIGHT}\nSelect an option from the list")
    print(Style.RESET_ALL)
    while True:
        if not(isUserLoggedIn):
            # Option to signup or login (When the user chooses signup for the first time there is no need to login)
            print(f"{YELLOW}1- {BLUE}Login\n{YELLOW}2- {BLUE}Signup\n")
            loginOption = '{}'.format(input(f"{MAGENTA}Enter a number: {YELLOW}{ITALIC}"))
            print(Style.RESET_ALL)
            if loginOption == "1":
                sendLoginRequest()
                continue
            elif loginOption == "2":
                sendSignupRequst()
                continue
            else:
                print(f"{RED}Invalid number")
                print(Style.RESET_ALL)
                continue
        print(f"{YELLOW}1- {BLUE}List Online Users\n{YELLOW}2- {BLUE}List Online Chatrooms\n{YELLOW}3- {BLUE}Create Chatroom\n{YELLOW}4- {BLUE}Join Chatroom\n{YELLOW}5- {BLUE}Private Chat\n{YELLOW}6- {BLUE}Reset Password\n{YELLOW}7- {BLUE}Logout\n")
        option = '{}'.format(input(f"{MAGENTA}Enter a number: {YELLOW}{ITALIC}"))
        print(Style.RESET_ALL)
        
        if option == "1":
            sendListOnlineUsersRequest()
            continue
        
        elif option == "2":
            print(f"{BRIGHT}Feature will be added later, stay tuned!")
            print(Style.RESET_ALL)
            
        elif option == "3":           
            peerNodeServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peerNodeServer.bind(('localhost', 0))
            peerPortNumber = peerNodeServer.getsockname()[1] # Gets the Port Number (Randomized by OS)

            responseCode, roomName = sendCreateChatroomRequest(peerPortNumber)

            peerNodeServer.listen()
            
            peerNodeListen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peerNodeListen.bind(('localhost', 0))
            peerIPListen = peerNodeListen.getsockname()[0]
            peerPortNumberListen = peerNodeListen.getsockname()[1]
            peerNodeListen.listen()
            
            lastFreePortNumber = peerPortNumberListen
            lastFreeIP = peerIPListen
            if responseCode == 1:
                handleChatRoomAdmin(roomName, peerNodeServer, peerNodeListen, peerPortNumberListen)
            elif responseCode == 0:
                peerNodeListen.close()
                
        elif option == "4":
            peerNodeAdmin = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peerNodeAdmin.bind(('localhost', 0))
            peerPortNumberAdmin = peerNodeAdmin.getsockname()[1]
            
            peerNodeListen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peerNodeListen.bind(('localhost', 0))
            peerPortNumberListen = peerNodeListen.getsockname()[1] # PORT number ready to listen to another peer
            peerNodeListen.listen()
            
            peerNodeSend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peerNodeSend.bind(('localhost', 0))
            peerPortNumberSend = peerNodeSend.getsockname()[1] # PORT number ready to send to another peer
            
            
            
            peerAdminIP, peerAdminPort, roomName = sendJoinChatroomRequest()
            if peerAdminIP != 0 and peerAdminPort != 0:
                peerNodeAdmin.connect((peerAdminIP, peerAdminPort))
                handleChatRoomPeer(peerNodeAdmin, roomName, peerPortNumberListen, peerNodeListen, peerNodeSend)
                
        elif option == "5":
            print(f"{BRIGHT}Feature will be added later, stay tuned!")
            print(Style.RESET_ALL)
        elif option == "6":
            sendResetPasswordRequst()
        elif option == "7":
            sendLogoutRequst()
        else:
            print(f"{RED}Invalid number")
            print(Style.RESET_ALL)
            continue
        

        



import socket
import threading
import hashlib
import time
from formats import *


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

def sendCreateChatroomRequest():
    # 1 -> room created successfully, 0 -> room creation failed 
    roomName = '{}'.format(input(f"{MAGENTA}Room Name: {YELLOW}{ITALIC}"))
    print(Style.RESET_ALL)
    print(f"{BRIGHT}Processing....")
    print(Style.RESET_ALL)

    message = f"CREATE_ROOM <{roomName}>"
    client.send(message.encode(FORMAT))
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if message == "ACCEPT 200":
                print(f"{BRIGHT}{GREEN}Room Created Successfully with namr {roomName}!")
                print(Style.RESET_ALL)
                return 1
            elif message == "NAME_EXISTS 403":
                print(f"{BRIGHT}{RED}Name of the room already exists, please try again.")
                print(Style.RESET_ALL)
                return 0
            elif message == "FAILED 500":
                print(f"{BRIGHT}{RED}An error has occured while creating the room, please try again.")
                print(Style.RESET_ALL)
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
            responseCode = sendCreateChatroomRequest()
            if responseCode == 1:
                pass
        elif option == "4":
            print(f"{BRIGHT}Feature will be added later, stay tuned!")
            print(Style.RESET_ALL)
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
        

        



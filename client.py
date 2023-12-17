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

client.connect(("197.52.196.173", 55050)) # Connect to the server

isUserLoggedIn = False

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

    username = '{}'.format(input('Username: '))
    password = '{}'.format(input('Password: '))
    print("Processing....")
    password = hashlib.sha256(password.encode()).hexdigest()
    message = f'LOGIN <{username}> <{password}>'
    client.send(message.encode(FORMAT))
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if message == "ACCEPT 200":
                isUserLoggedIn = True
                print("Login Success!")
                return
            elif message == "NOT_FOUND 401":
                print("The username does not exist in the database, please try again.")
                return
            elif message == "INCORRECT_PASSWORD 402":
                print("Incorrect Password Entered, please try again.")
                return
            elif message == "FAILED 500":
                print("An error has occured while logging you in, please try again.")
                return
        except:
            print("An error occured with the connection!")
            client.close()
            break

def sendSignupRequst():
    global isUserLoggedIn

    username = '{}'.format(input('Username: '))
    password = '{}'.format(input('Password: '))
    print("Processing....")
    password = hashlib.sha256(password.encode()).hexdigest()
    message = f'CREATE <{username}> <{password}>'
    client.send(message.encode(FORMAT))
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if message == "ACCEPT 200":
                isUserLoggedIn = True
                print("Account Created Successfully!")
                return
            elif message == "USERNAME_TAKEN 400":
                print("The username already exists in the database, please try again.")
                return
            elif message == "FAILED 500":
                print("An error has occured while creating an account, please try again.")
                return
        except:
            print("An error occured with the connection!")
            client.close()
            break

def sendLogoutRequst():
    global isUserLoggedIn

    message = 'LOGOUT'
    client.send(message.encode(FORMAT))
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if message == "ACCEPT 200":
                isUserLoggedIn = False
                print("Logged Out Successfully!")
                return
            elif message == "FAILED 500":
                print("An error has occured while logging out, please try again.")
                return
        except:
            print("An error occured with the connection!")
            client.close()
            break

if __name__ == "__main__":
    # receive_thread = threading.Thread(target=receiveMessageFromServer)
    # receive_thread.start()
    print("Welcome to ASU Chatrooms!\nSelect an option from the list")
    while True:
        if not(isUserLoggedIn):
            # Option to signup or login (When the user chooses signup for the first time there is no need to login)
            print("1- Login\n2- Signup\n")
            loginOption = '{}'.format(input('Enter a number: '))
            if loginOption == "1":
                sendLoginRequest()
                continue
            elif loginOption == "2":
                sendSignupRequst()
                continue
            else:
                print("Invalid number")
                continue
        print("1- List Online Users\n2- List Online Chatrooms\n3- Create Chatroom\n4- Join Chatroom\n5- Private Chat\n6- Logout")
        option = '{}'.format(input('Enter a number: '))
        if option == "1":
            print("Feature will be added later, stay tuned!")
        elif option == "2":
            print("Feature will be added later, stay tuned!")
        elif option == "3":
            print("Feature will be added later, stay tuned!")
        elif option == "4":
            print("Feature will be added later, stay tuned!")
        elif option == "5":
            print("Feature will be added later, stay tuned!")
        elif option == "6":
            sendLogoutRequst()
        else:
            print("Invalid number")
            continue
        

        # write_thread = threading.Thread(target=sendMessageToServer)
        # write_thread.start()



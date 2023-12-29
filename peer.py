import re
import threading
import socket
import time
from formats import MAGENTA, WHITE, Style, BLUE, RED, ITALIC, YELLOW, BRIGHT, GREEN, CYAN
FORMAT = 'utf-8' # Message Encoding Format
peersConnected = []
peersConnectedAdmin = []
lastFreePortNumber = None
lastFreeIP = None

class Peer:
    def __init__(self, username, ip_address, port_number):
        self.username = username
        self.ip_address = ip_address
        self.port_number = port_number  # UDP Socket to Broadcast Messages

class PeerAdmin:
    def __init__(self, username, ip_address, udp_port_number, peer_listen_port):
        self.username = username
        self.ip_address = ip_address
        self.udp_port_number = udp_port_number  # UDP Socket to Broadcast Messages
        self.peer_listen_port = peer_listen_port # Address to send to from admin
        

def deleteChatRoomRequest(chatRoomName, client):
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

def connectToAdmin(peerNodeAdmin, broadcastUDPPort, peerNodeListenPort, username):
    # 0 means room created successfully, 1 means request declined or error occurred
    global peersConnected
    message = f"REQUEST_JOIN <{username}> <{broadcastUDPPort}> <{peerNodeListenPort}>"
    peerNodeAdmin.send(message.encode(FORMAT))
    while True:
        try:
            message = peerNodeAdmin.recv(1024).decode(FORMAT).split(" ")
            if message[0] == "ACCEPT" and message[1] == "200":
                message[2] = message[2].replace("<", '')
                message[2] = message[2].replace(">", '')
                usernamesList = [word for word in message[2].split(",") if word] # Split the message into a list
                
                message[3] = message[3].replace("<", '')
                message[3] = message[3].replace(">", '')
                IPList = [word for word in message[3].split(",") if word] # Split the message into a list
                
                message[4] = message[4].replace("<", '')
                message[4] = message[4].replace(">", '')
                portList = [word for word in message[4].split(",") if word] # Split the message into a list
                
                for i in range(len(usernamesList)):
                    peersConnected.append(Peer(username = usernamesList[i], ip_address = IPList[i], port_number = portList[i]))
                print(f"{BRIGHT}{GREEN}Request to join room accepted!{Style.RESET_ALL}")
                return 0
            elif message == "FAILED 500":
                print(f"{BRIGHT}{RED}Request to join room declined!{Style.RESET_ALL}")
                return 1
        except Exception as e:
            print(e)   
            print(f"{BRIGHT}{RED}An error occured with the connection!{Style.RESET_ALL}")
            peerNodeAdmin.close()
            return 1
        
def listenToAdmin(peerNodeListen):
    
    while True:
        try:
            admin, address = peerNodeListen.accept()
            thread = threading.Thread(target=processAdminRequest, args=(admin,))
            thread.start()
                    
        except Exception as e:
            print("dddd")
            print(e)
            pass
        
def processAdminRequest(admin):
    global peersConnected
    while True:
        try:
            messageReceived = admin.recv(1024).decode(FORMAT).split(" ")
            if messageReceived[0] == "NEW_CONNECTION":
                username = re.search(r'<(.*?)>', messageReceived[1]).group(1)
                ip = re.search(r'<(.*?)>', messageReceived[2]).group(1)
                port = int(re.search(r'<(.*?)>', messageReceived[3]).group(1))
                print(f"{BRIGHT}{MAGENTA}{username} have joined the room!{Style.RESET_ALL}")
                peersConnected.append(Peer(username = username, ip_address = ip, port_number = port))
                
            elif messageReceived[0] == "KICK":
                print(f"{BRIGHT}{MAGENTA}You have been kicked from the room type anything to return to menu!{Style.RESET_ALL}")
                peersConnected = []
                return
        except Exception as e:
            print(e)
            
            

def listenToPeers(broadcastUDP):
    global peersConnected
    while True:
        try:
            data, _ = broadcastUDP.recvfrom(1024)
            decoded_data = data.decode(FORMAT).split(" ")
            
            if decoded_data[0] == "SEND_MESSAGE":
                username = re.search(r'<(.*?)>', decoded_data[1]).group(1)
                message = re.search(r'<(.*?)>', decoded_data[2]).group(1)
                print(f"{BLUE}{username}: {WHITE}{message}{Style.RESET_ALL}")
            if len(peersConnected) == 0:
                broadcastUDP.close()
                return
        except Exception as e:
            print("momken")
            print(e)
            
def sendMessageChatRoom(peerNodeListen, myUsername):
    global peersConnected
    sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockUDP.bind(('localhost', 0))
    print(f"{BLUE}You can type {RED}!back{BLUE} to exit the chatroom!")
    while True:
        try:
            message = '{}'.format(input(f"{Style.RESET_ALL}{YELLOW}{ITALIC}"))
            if message == "!back":
                peersConnected = []
                sockUDP.close()
                peerNodeListen.close()
                return
            else:
                for i in range(len(peersConnected)):
                    sockUDP.sendto(f"SEND_MESSAGE <{myUsername}> <{message}>".encode(FORMAT), (peersConnected[i].ip_address, int(peersConnected[i].port_number)))
                
        except Exception as e: 
            sockUDP.close()
            print("?")
            print(e)

def acceptPeersAdmin(peerNodeServer, clientUsername, broadcastUDPPort, myIP):
    while True:
        try:
            peer, address = peerNodeServer.accept()
            thread = threading.Thread(target=acceptPeerRequest, args=(peer, address, clientUsername, broadcastUDPPort, myIP,))
            thread.start()
        except:
            pass
        
def acceptPeerRequest(peerNodeRespond, address, clientUsername, broadcastUDPPort, myIP):
    global peersConnectedAdmin
    ip, port = address
    while True:
            messageReceived = peerNodeRespond.recv(1024).decode(FORMAT).split(" ")
            if messageReceived[0] == "REQUEST_JOIN":
                username = re.search(r'<(.*?)>', messageReceived[1]).group(1)
                udpPort = int(re.search(r'<(.*?)>', messageReceived[2]).group(1))
                listenPort = re.search(r'<(.*?)>', messageReceived[3]).group(1)
                
                print(f"{YELLOW}{username} {BLUE}wants to join the room type {RED}!respond {BLUE}to respond and then type {YELLOW}Yes {BLUE}or {YELLOW}No{Style.RESET_ALL}")
                response = '{}'.format(input(f"{MAGENTA}Decision: {YELLOW}{ITALIC}"))
                if response == "Yes" or response == "yes" or response == "y" or response == "Y":
                    usernames = []
                    IPS = []
                    ports = []
                    for peer in peersConnectedAdmin:
                        usernames.append(peer.username)
                        IPS.append(peer.ip_address)
                        ports.append(peer.udp_port_number)
                        peerNode = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        peerNode.bind(('localhost', 0))
                        peerNode.connect((peer.ip_address, int(peer.peer_listen_port)))
                        peerNode.send(f"NEW_CONNECTION <{username}> <{ip}> <{udpPort}>".encode(FORMAT))
                        peerNode.close()
                    usernames.append(clientUsername)
                    IPS.append(myIP)
                    ports.append(int(broadcastUDPPort))
                    usernames_string = ','.join(usernames)
                    IPS_string = ','.join(IPS)
                    ports_string = ','.join(map(str, ports))
                    peersConnectedAdmin.append(PeerAdmin(username = username, ip_address = ip, udp_port_number = udpPort, peer_listen_port = listenPort))
                    peerNodeRespond.send(f"ACCEPT 200 <{usernames_string}> <{IPS_string}> <{ports_string}>".encode(FORMAT)) 
                else:
                    print(f"{MAGENTA}You rejected the join request!{Style.RESET_ALL}")
                    peerNode.send(f"FAILED 500".encode(FORMAT))
    
def listenToPeersAsAdmin(broadcastUDP):
    while True:
        try:
            data, _ = broadcastUDP.recvfrom(1024)
            decoded_data = data.decode(FORMAT).split(" ")
            if decoded_data[0] == "SEND_MESSAGE":
                username = re.search(r'<(.*?)>', decoded_data[1]).group(1)
                message = re.search(r'<(.*?)>', decoded_data[2]).group(1)
                print(f"{BLUE}{username}: {WHITE}{message}{Style.RESET_ALL}")
        except Exception as e:
            print("maybeeee")
            print(e)
            

def sendMessageChatroomAdmin(myUsername, roomName, client):
    global peersConnectedAdmin
    sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockUDP.bind(('localhost', 0))
    print(f"{MAGENTA}Commands:\n{YELLOW}!back {CYAN}To exit the chatroom and delete it.\n{YELLOW}!kick username {CYAN}To kick someone from the room\n{YELLOW}!respond {CYAN}To accept or decline the join request{Style.RESET_ALL}")
    while True:
        try:
            message = '{}'.format(input(f"{Style.RESET_ALL}{YELLOW}{ITALIC}"))
            if message == "!back":
                deleteChatRoomRequest(roomName, client)
                return
            elif message == "!kick":
                pass
            elif message == "!respond":
                time.sleep(5)
            else:
                for i in range(len(peersConnectedAdmin)):
                    sockUDP.sendto(f"SEND_MESSAGE <{myUsername}> <{message}>".encode(FORMAT), (peersConnectedAdmin[i].ip_address, int(peersConnectedAdmin[i].udp_port_number)))
        except Exception as e:
            print("hena yaba")
            print(e)
            pass
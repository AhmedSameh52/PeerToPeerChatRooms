import re
import threading
import socket
import time
from formats import MAGENTA, WHITE, Style, BLUE, RED, ITALIC, YELLOW, BRIGHT, GREEN, CYAN
FORMAT = 'utf-8' # Message Encoding Format
peersConnected = []
lastFreePortNumber = None
lastFreeIP = None
class Peer:
    def __init__(self, username, ip_address, port_number, peerNode):
        self.username = username
        self.ip_address = ip_address
        self.port_number = port_number  # Same as accept_peer_port_number
        self.peerNode = peerNode
        
def peerReceive(peerNode, IPToConnect, PortNumberToConnect, connectFirst):
    global peersConnected
    
    if connectFirst:
        peerNode.connect((IPToConnect, PortNumberToConnect)) # Connect to the other peer defined by admin
        peersConnected.insert(0,Peer(username = "NA", ip_address = IPToConnect, port_number = PortNumberToConnect, peerNode = peerNode))
    else:
        peersConnected.append(Peer(username = "NA", ip_address = IPToConnect, port_number = PortNumberToConnect, peerNode = peerNode))
    while True:
            try:
                messageReceived = peerNode.recv(1024).decode(FORMAT)
                messageRecivedList = messageReceived.split(" ")
                if messageRecivedList[0] == "SEND_MESSAGE":
                    peerUsername = re.search(r'<(.*?)>', messageRecivedList[1]).group(1)
                    message = re.search(r'<(.*?)>', messageRecivedList[2]).group(1)
                    
                    for i,peer in enumerate(peersConnected):
                        if peer.peerNode == peerNode:
                            peersConnected[i].username = peerUsername
                            continue
                        peer.peerNode.send(messageReceived.encode(FORMAT))
                    print(f"{MAGENTA}{peerUsername}: {WHITE}{message}")
                    print(Style.RESET_ALL)
            except:
                break

def peerListen(peerNodeListen):
     while True:
        try:
            peerConnection, address = peerNodeListen.accept()
            ip, port = address
            thread = threading.Thread(target=peerReceive, args=(peerConnection, ip, port, False,))
            thread.start()
            
        except:
            pass

def sendLeaveRoomCommand(peerNodeAdmin, clientUsername):
    global peersConnected
    ip2 = None
    port2 = None
    ip1 = peersConnected[0].ip_address
    port1 = peersConnected[0].port_number
    message = f"LEAVE_ROOM <{clientUsername}> <{ip1}> <{port1}> <NA> <-1>"
    if len(peersConnected) == 2:
        ip2 =  peersConnected[1].ip_address
        port2 = peersConnected[1].port_number
        message = f"LEAVE_ROOM <{clientUsername}> <{ip1}> <{port1}> <{ip2}> <{port2}>"

    peerNodeAdmin.send(message.encode(FORMAT))
   
def peerSend(isAdmin, roomName, thread, threadListen, peerNodeAdmin, client, clientUsername):
    global peersConnected
    if isAdmin:
        print(f"{BLUE}To exit the chat room type {RED}{ITALIC}!back{Style.RESET_ALL}{BLUE},the room will be deleted afterwards!{Style.RESET_ALL}")
    else:
        print(f"{BLUE}To exit the chat room type {RED}{ITALIC}!back{Style.RESET_ALL}{BLUE}{Style.RESET_ALL}")
    while True:
        message = '{}'.format(input(f"{YELLOW}{ITALIC}"))
        messageToBeSent = f"SEND_MESSAGE <{clientUsername}> <{message}>"
        if message == "!back":
            if isAdmin:
                deleteChatRoomRequest(roomName, client)
            sendLeaveRoomCommand(peerNodeAdmin, clientUsername)
            thread.join(timeout=1)
            threadListen.join(timeout=1)
            return     
        elif message == "!respond":
            # time.sleep(5)
            pass
        indexToRemove = None
        for i,peer in enumerate(peersConnected):
            try:
                peer.peerNode.send(messageToBeSent.encode(FORMAT))
            except:
                indexToRemove = i
                continue
        if indexToRemove != None:
            del peersConnected[indexToRemove]
        print(f"{Style.RESET_ALL}{YELLOW}{clientUsername}: {MAGENTA}{message}{Style.RESET_ALL}")
 
def handleChatRoomPeer(peerNodeAdmin, roomName, peerPortNumberListen, peerNodeListen, peerNodeSend, client, clientUsername):
    global peersConnected
    try:
        threadSend = None
        message = f"JOIN_ROOM_REQUEST <{clientUsername}> <{peerPortNumberListen}>"
        peerNodeAdmin.send(message.encode(FORMAT))
        while True:
            message = peerNodeAdmin.recv(1024).decode(FORMAT).split(" ")
            if message[0] == "REQUEST_ACCEPTED" and message[1] == "201":
                print(f"{BRIGHT}{GREEN}Request to Join Accepted.")
                print(Style.RESET_ALL)
                
                IPToConnect = re.search(r'<(.*?)>', message[2]).group(1)
                PortNumberToConnect = int(re.search(r'<(.*?)>', message[3]).group(1))
                thread = threading.Thread(target=peerReceive, args=(peerNodeSend, IPToConnect, PortNumberToConnect, True,))
                thread.start()
                threadListen = threading.Thread(target=peerListen, args=(peerNodeListen,))
                threadListen.start()
                
                threadSend = threading.Thread(target=peerSend, args=(False, roomName, thread, threadListen, peerNodeAdmin, client, clientUsername,))
                threadSend.start()
                               
                    
            elif message[0] == "REQUEST_DECLINED" and message[1] == "406":
                print(f"{BRIGHT}{RED}Request to Join Declined.")
                print(Style.RESET_ALL)
                peerNodeAdmin.close()
                
                return
            elif message[0] == "REDIRECT":
                newIP = re.search(r'<(.*?)>', message[1]).group(1)
                newPort = int(re.search(r'<(.*?)>', message[2]).group(1))
                peersConnected[0].peerNode.close()
                peersConnected.pop(0)
                peerNodeSend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peerNodeSend.bind(('localhost', 0))
                peerPortNumberSend = peerNodeSend.getsockname()[1] # New Port Number
                thread = threading.Thread(target=peerReceive, args=(peerNodeSend, newIP, newPort, True,))
                thread.start()
                
            elif message[0] == "LEAVE_ACCEPTED" and message[1] == "202":
                peerNodeAdmin.close()
                peerNodeListen.close()
                peerNodeSend.close()
                peersConnected = []
                return
                
            elif message[0] == "FAILED" and message[1] == "500":
                print(f"{BRIGHT}{RED}An error has occured while joining the room, please try again.")
                print(Style.RESET_ALL)
                peerNodeAdmin.close()
                return
    except:
        print(f"{BRIGHT}{RED}An error has occured while joining the room, please try again.")
        print(Style.RESET_ALL)
        peerNodeAdmin.close()
        return

def handleChatRoomAdmin(roomName, peerNodeServer, peerNodeListen, peerIPListen, peerPortNumberListen, client, clientUsername):
    global lastFreePortNumber
    global lastFreeIP
    lastFreePortNumber = peerPortNumberListen
    lastFreeIP = peerIPListen
    thread = threading.Thread(target=acceptInvitations, args=(peerNodeServer, client,))
    thread.start()
    threadListen = threading.Thread(target=peerListen, args=(peerNodeListen,))
    threadListen.start()
    peerSend(True, roomName, thread, threadListen, peerNodeListen, client, clientUsername)
    return

def acceptInvitations(peerNodeServer, client):
    global peersConnected
    while True:
        try:
            peerConnection, address = peerNodeServer.accept()
            ip, port = address
            peersConnected.append(Peer(username = "NA", ip_address = ip, port_number = port, peerNode = peerConnection))
            thread = threading.Thread(target=acceptPeers, args=(peerConnection, address, client, ))
            thread.start()
            
        except:
            pass
        
def acceptPeers(peerConnection, address, client):
    global lastFreePortNumber
    global lastFreeIP
    global peersConnected
    ip, port = address
    while True:
        try:
            messageReceived = peerConnection.recv(1024).decode(FORMAT).split(" ")
            if messageReceived[0] == "JOIN_ROOM_REQUEST":
                peerUsername = re.search(r'<(.*?)>', messageReceived[1]).group(1)
                freePortNumber = int(re.search(r'<(.*?)>', messageReceived[2]).group(1))
                
                print(f"{BLUE}User {GREEN}{peerUsername} {BLUE}want to join your room! Type {MAGENTA}Yes{BLUE} to accept the invitation or {MAGENTA}No {BLUE}to reject it")
                print(f"{BLUE}Type {RED}!respond{BLUE} in the chat to respond to the message")
                print(Style.RESET_ALL)
                decision = '{}'.format(input(f"{YELLOW}{ITALIC}"))
                print(Style.RESET_ALL)
                
                if decision == "Yes" or decision == "yes" or decision == "y" or decision == "Y":
                    peerConnection.send(f"REQUEST_ACCEPTED 201 <{lastFreeIP}> <{lastFreePortNumber}>".encode(FORMAT))
                    lastFreePortNumber = freePortNumber
                    lastFreeIP = ip
                elif decision == "No" or decision == "no" or decision == "n" or decision == "N":
                    peerConnection.send('REQUEST_DECLINED 406'.encode(FORMAT))
                    peerConnection.close()
            elif messageReceived[0] == "LEAVE_ROOM":
                try:
                    peerUsername = re.search(r'<(.*?)>', messageReceived[1]).group(1)
                    ipWasConnectedTo = re.search(r'<(.*?)>', messageReceived[2]).group(1)
                    portWasConnectedTo = int(re.search(r'<(.*?)>', messageReceived[3]).group(1))
                    ipWasListeningTo = re.search(r'<(.*?)>', messageReceived[4]).group(1)
                    portWasListeningTo = int(re.search(r'<(.*?)>', messageReceived[5]).group(1))
                    if ipWasListeningTo == "NA":
                        # This is the last node
                        lastFreePortNumber = portWasConnectedTo
                        lastFreeIP = ipWasConnectedTo
                    else:
                        responseCode = sendRedirectRequestToConnectedNode(ipWasListeningTo, portWasListeningTo, ipWasConnectedTo, portWasConnectedTo, client)
                    peerConnection.send("LEAVE_ACCEPTED 202".encode(FORMAT))
                    # for i,peer in enumerate(peersConnected):
                    #     if peerUsername == peer.username:
                    #         del peersConnected[i]
                except:
                    peerConnection.send("FAILED 500".encode(FORMAT))
                    
                    
        except:
            peerConnection.close()

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


def sendRedirectRequestToConnectedNode(ipWasListeningTo, portWasListeningTo, ipWasConnectedTo, portWasConnectedTo, client):
    print(33333)
    global peersConnected
    # Get the connected node
    for peer in peersConnected:
        if (ipWasListeningTo == peer.ip_address) and (portWasListeningTo == peer.port_number):
            message = f"REDIRECT <{ipWasConnectedTo}> <{portWasConnectedTo}>"
            peer.peerNode.send(message.encode(FORMAT))
            while True:
                try:
                    messageReceived = client.recv(1024).decode(FORMAT)
                    if message == "ACCEPT 200":
                        return 0
                    elif message == "FAILED 500":
                        return 1
                except:   
                    print(f"{BRIGHT}{RED}An error occured with the connection!")
                    print(Style.RESET_ALL)
                    peer.peerNode.close()
                    return 1

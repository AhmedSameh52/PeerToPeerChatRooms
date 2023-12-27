class User:
    def __init__(self, username, password, ip_address, port_number, accept_peer_port_number):
        self.username = username
        self.password = password
        self.ip_address = ip_address
        self.port_number = port_number
        self.accept_peer_port_number = accept_peer_port_number
        self.helloTimerRemaining = 5
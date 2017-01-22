import socket
import json
import time
import asyncore
import logging

logging.basicConfig(filename='server.log',level=logging.DEBUG)
REQ = 'REQ'
REL = 'REL'
REP = 'REP'
CLIREQ = 'CLIREQ'


# class Server:

# 	def initialize(self, dcId, config):
		
# 		ip, port = config["datacenters"][dcId][0], config["datacenters"][dcId][1]

# 		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 		#s.setblocking(0)
# 		s.bind((ip, port))
# 		s.listen(1)
# 		while True:
# 			conn, addr = s.accept()
# 			print('Connected by ', addr)
# 			recvMsg = conn.recv(4096)
# 			print(recvMsg)
# 			'''Keep reaceving data as long as data is being sent.'''
# 			#while True:
# 		  	#  data = conn.recv(1024)
# 		    #  if not data: break
# 		    #  recvMsg += data

# 			msgType, dcId, noOfTickets = self.parseRecvMsg(recvMsg)
# 			time.sleep(30)
# 			'''Perform appropriate action based on type of message received'''
# 			if msgType == REQ:
# 				print REQ
# 			elif msgType == REP:
# 				print REP
# 			elif msgType == REL:
# 				print REL
# 			elif msgType == CLIREQ:
# 				print CLIREQ

# 			time.sleep(5)
# 			conn.send(recvMsg)
# 			conn.close()

class Tickets:
	def __init__(self, tickets):
		self.tickets = tickets
class Server(asyncore.dispatcher):
    """Receives connections and establishes handlers for each client.
    """

    
    def __init__(self, dcId, config):

        self.logger = logging.getLogger('EchoServer')
        ip, port = config["datacenters"][dcId][0], config["datacenters"][dcId][1]
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((ip, port))
        self.address = self.socket.getsockname()
        self.logger.debug('binding to %s', self.address)
        self.listen(5)
        self.tickets = Tickets(10)
        return

    def handle_accept(self):
        # Called when a client connects to our socket
        client_info = self.accept()
        self.logger.debug(str(time.time()) + 'handle_accept() -> %s', client_info[1])
        print 'Accepted'
        Handler(sock=client_info[0], tickets=self.tickets)
        #self.handle_close()
        return
    
    def handle_close(self):
        self.logger.debug('handle_close()')
        self.close()
        return

class Handler(asyncore.dispatcher):
    """Handles echoing messages from a single client.
    """
    
    def __init__(self, sock, tickets, chunk_size=4096):
    	tickets.tickets = tickets.tickets-1
        self.chunk_size = chunk_size
        self.data_to_write = ''
        self.logger = logging.getLogger('Handler%s' % str(sock.getsockname()))
        asyncore.dispatcher.__init__(self, sock=sock)
        print tickets.tickets
        return

    def parseRecvMsg(self, recvMsg):
		msgType, dcId, noOfTickets = recvMsg.split(':')[0], \
								recvMsg.split(':')[1].split(',')[0], \
								recvMsg.split(':')[1].split(',')[1]

		return msgType, dcId, noOfTickets

    def writable(self):
        """We want to write if we have received data."""
        response = bool(self.data_to_write)
        self.logger.debug('writable() -> %s', response)
        return response
    
    def handle_write(self):
        """Write as much as possible of the most recent message we have received."""
        data = self.data_to_write
        sent = self.send(data)
        self.logger.debug('handle_write() -> "%s"', data)
        #if not self.writable():
        self.handle_close()

    def handle_read(self):
        """Read an incoming message from the client and put it into our outgoing queue."""
        recvMsg = self.recv(self.chunk_size)
        #We may have to add sleep
        if not recvMsg:
        	self.handle_close()
        self.logger.debug('handle_read() -> "%s"', recvMsg)

        msgType, dcId, noOfTickets = self.parseRecvMsg(recvMsg)
        time.sleep(30)
        '''Perform appropriate action based on type of message received'''
        if msgType == REQ:
        	print REQ
        elif msgType == REP:
        	print REP
        elif msgType == REL:
        	print REL
        elif msgType == CLIREQ:
        	#self.handleClientRequest()
        	print CLIREQ

		self.data_to_write = "From server: " + recvMsg

	def handle_close(self):
		self.logger.debug('handle_close()')
		self.close()


	#def handleClientRequest(self):

with open('server_config.json') as data_file:    
    data = json.load(data_file)
s = Server('dc1', data)
asyncore.loop()
import socket
import json
import time
import asyncore

REQ = 'REQ'
REL = 'REL'
REP = 'REP'
CLIREQ = 'CLIREQ'


class Server:

	def parseRecvMsg(self, recvMsg):
		msgType, dcId, noOfTickets = recvMsg.split(':')[0], \
								recvMsg.split(':')[1].split(',')[0], \
								recvMsg.split(':')[1].split(',')[1]

		return msgType, dcId, noOfTickets

	def initialize(self, dcId, config):
		
		ip, port = config["datacenters"][dcId][0], config["datacenters"][dcId][1]

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#s.setblocking(0)
		s.bind((ip, port))
		s.listen(1)
		while True:
			conn, addr = s.accept()
			print('Connected by ', addr)
			recvMsg = conn.recv(4096)
			print(recvMsg)
			'''Keep reaceving data as long as data is being sent.'''
			#while True:
		  	#  data = conn.recv(1024)
		    #  if not data: break
		    #  recvMsg += data

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
				print CLIREQ

			time.sleep(5)
			conn.send(recvMsg)
			conn.close()

s = Server()
with open('server_config.json') as data_file:    
    data = json.load(data_file)
s.initialize('dc1', data)
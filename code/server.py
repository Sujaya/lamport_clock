import socket 
from threading import Thread 
from SocketServer import ThreadingMixIn 
import time
import threading
import json, sys
import logging
import sys


with open('server_config.json') as config_file:    
    config = json.load(config_file)
selfDcId = sys.argv[1]

dcInfo= {'dc_name':selfDcId.upper()}

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
formatter = logging.Formatter('%(dc_name)s: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger = logging.LoggerAdapter(logger, dcInfo)


REQ = 'REQ'
REL = 'REL'
REP = 'REP'
CLIREQ = 'CLIREQ'


delay = config['delay']


class MutexInfo:
	def __init__(self, seqNo, procId, selfDcId, conn=None):
		self.clock = {'seqNo':seqNo, 'procId':procId}
		self.totalTickets = config['tickets']
		self.totalDCs = len(config['datacenters'])
		#prQueue = [(dc1, Clock), (dc2, Clock)]
		self.prQueue = []
		self.waitingForRelease = False
		self.selfDcId = selfDcId
		self.requestedNoOfTickets = 0
		self.clientConn = conn


	def comparator(self, tup1, tup2):
		clockA, clockB = tup1[1], tup2[1]
		if clockA['seqNo'] < clockB['seqNo']:
			return -1
		elif clockA['seqNo'] == clockB['seqNo'] and clockA['procId'] < clockB['procId']:
			return -1
		return 1


# Multithreaded Python server : TCP Server Socket Thread Pool
class ClientThread(Thread): 
 
	def __init__(self, conn, ip, port, mutexinfo): 
		Thread.__init__(self) 
		self.ip = ip 
		self.port = port 
		self.conn = conn
		self.mutexinfo = mutexinfo
		#print "[+] New server socket thread started for " + ip + ":" + str(port) 
 
	def run(self): 
		cliReq = False
		conn, recvMsg = self.conn, self.conn.recv(2048)
		logMsg = 'Received message from: (%s:%d). Message is: %s' %(self.ip, self.port, recvMsg)
		logger.debug(logMsg)

		msgType, dcId, noOfTickets, clock = self.parseRecvMsg(recvMsg)
		self.updateClock(self.mutexinfo.clock['seqNo'], clock['seqNo'])

		if msgType==CLIREQ:
			cliReq = True
			clock = dict(self.mutexinfo.clock)
			self.handleClientReq(noOfTickets, clock)
		elif msgType == REQ:
			self.handleDatacenterReq(dcId, noOfTickets, clock)
		elif msgType == REP:
			self.handleReplyMsg()
		elif msgType == REL:
			self.handleReleaseMsg(dcId, noOfTickets)

		if not cliReq:
			conn.close() 
		sys.exit()


	def parseRecvMsg(self, recvMsg):
		msgType, dcId, noOfTickets, clock = recvMsg.split('::')[0], \
						recvMsg.split('::')[1].split(',')[0], \
						recvMsg.split('::')[1].split(',')[1], \
						recvMsg.split('::')[1].split(',', 2)[2]
		
		clock = json.loads(clock)
		return msgType, dcId, int(noOfTickets), clock


	def sendTcpMsg(self, ip, port, msg):
		tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		time.sleep(delay)
		tcpClient.connect((ip, port))
		tcpClient.send(msg)
		logMsg = 'Sent message to: (%s, %d). Message is: %s' %(ip, port, msg)
		logger.debug(logMsg)


	def updateClock(self, seqNo1, seqNo2):
		#increment clock value by finding max of current dc and sent dc + 1
		self.mutexinfo.clock['seqNo'] = max(seqNo1, seqNo2) + 1
		logMsg = 'Updated clock values to %d:%d' %(self.mutexinfo.clock['seqNo'], self.mutexinfo.clock['procId'])
		logger.debug(logMsg)

	def addAndUpdateQueue(self, dcId, clock):
		self.mutexinfo.prQueue.append((dcId, clock))
		self.mutexinfo.prQueue.sort(cmp=self.mutexinfo.comparator)
		logMsg = 'Updated queue to %s' %repr(self.mutexinfo.prQueue)
		logger.debug(logMsg)

	def popAndUpdateQueue(self):
		self.mutexinfo.prQueue.pop(0)
		logMsg = 'Updated queue to %s' %repr(self.mutexinfo.prQueue)
		logger.debug(logMsg)


	def handleClientReq(self, noOfTickets, clock):
		self.mutexinfo.clientConn = self.conn
		if self.mutexinfo.totalTickets - noOfTickets < 0:
			self.replyToClient(self.mutexinfo.totalTickets, success=False)
			return

		self.mutexinfo.requestedNoOfTickets = noOfTickets
		
		self.addAndUpdateQueue(self.mutexinfo.selfDcId, clock)
		for dcId in config["datacenters"]:
			if dcId == self.mutexinfo.selfDcId:
				continue
			ip, port = config["datacenters"][dcId][0], config["datacenters"][dcId][1]
			reqMsg = 'REQ::'+self.mutexinfo.selfDcId+','+str(noOfTickets)+','+json.dumps(clock)
			self.sendTcpMsg(ip, port, reqMsg)


	def handleDatacenterReq(self, dcId, noOfTickets, clock):
		# Queue appropriately and reply
		self.addAndUpdateQueue(dcId, clock)
		ip, port = config["datacenters"][dcId][0], config["datacenters"][dcId][1]
		repMsg = 'REP::'+self.mutexinfo.selfDcId+','+str(noOfTickets)+','+json.dumps(self.mutexinfo.clock)
		self.sendTcpMsg(ip, port, repMsg)


	def handleReplyMsg(self):
		self.mutexinfo.totalDCs -= 1
		
		if self.mutexinfo.totalDCs == 1:
			self.accessTickets()

	def resetVariables(self):
		#reset all variables
		self.mutexinfo.requestedNoOfTickets = 0
		self.mutexinfo.waitingForRelease = False
		self.mutexinfo.totalDCs = len(config['datacenters'])


	def accessTickets(self):
		
		# Check for top of Queue; if I am at top, reduct tickets value
		if self.mutexinfo.prQueue[0][0] == self.mutexinfo.selfDcId:
			success = False
			if self.mutexinfo.totalTickets - self.mutexinfo.requestedNoOfTickets >= 0:
				self.mutexinfo.totalTickets -= self.mutexinfo.requestedNoOfTickets
				logMsg = 'Updated tickets value to %d' %self.mutexinfo.totalTickets
				logger.debug(logMsg)
				success = True

			currTickets = self.mutexinfo.totalTickets

			self.resetVariables()
			#pop from mine and release to other DCs
			self.popAndUpdateQueue()
			self.sendReleaseMsg(currTickets)

			#reply to client
			self.replyToClient(currTickets, success=success)
		else:
			logMsg = 'Waiting for other DCs to release.'
			logger.debug(logMsg)
			self.mutexinfo.waitingForRelease = True


	def replyToClient(self, currTickets, success):
		if not success:
			cliReply = 'Total tickets available: '+str(currTickets)+'. Tickets requested should be less that total tickets available.'
			 			
		else:
			cliReply = 'Successfully purchased tickets. Total remaining tickes are ' +str(currTickets)
			 			
		self.mutexinfo.clientConn.send(cliReply)
		self.mutexinfo.clientConn.close()
		self.mutexinfo.clientConn = None


	def sendReleaseMsg(self, tickets):
		clock = dict(self.mutexinfo.clock)
		for dcId in config["datacenters"]:
			if dcId == self.mutexinfo.selfDcId:
				continue
			ip, port = config["datacenters"][dcId][0], config["datacenters"][dcId][1]
			relMsg = 'REL::'+self.mutexinfo.selfDcId+','+str(tickets)+','+json.dumps(clock)
			self.sendTcpMsg(ip, port, relMsg)


	def handleReleaseMsg(self, dcId, noOfTickets):
		self.mutexinfo.totalTickets = min(self.mutexinfo.totalTickets, noOfTickets)
		logMsg = 'Received updated ticket value. Updating tickets value to %d' %self.mutexinfo.totalTickets
		logger.debug(logMsg)
		#pop dcid from queue
		self.popAndUpdateQueue()
		if self.mutexinfo.waitingForRelease:
			self.accessTickets()

######################################## Main ################################################



ip, port = config["datacenters"][selfDcId][0], config["datacenters"][selfDcId][1]

tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
tcpServer.bind((ip, port))

mutexinfo = MutexInfo(0, int(selfDcId[2:]), selfDcId)
threads = [] 
print 'Server ready to listen on (%s:%d)' %(ip, port)
while True: 
    tcpServer.listen(4) 
    (conn, (cliIP,cliPort)) = tcpServer.accept() 
    newthread = ClientThread(conn, cliIP, cliPort, mutexinfo) 
    newthread.start()
    threads.append(newthread) 
 

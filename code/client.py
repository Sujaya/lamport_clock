import socket
import time
import asyncore
import logging
logging.basicConfig(filename='client.log',level=logging.DEBUG)
# class Client:
#     def buyTickets(self, dcId, dcInfo, noOfTickets):

#         ip, port = dcInfo[0], dcInfo[1]
#         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         s.connect((ip, port))
#         time.sleep(30)
#         reqMsg = 'CLIREQ:'+dcId+','+str(noOfTickets)
#         s.send(reqMsg)
#         data = s.recv(4096)
#         s.close()
#         print('Received', repr(data))

class Client(asyncore.dispatcher):
    """Sends messages to the server and receives responses.
    """
    
    def buyTickets(self, dcId, dcInfo, noOfTickets):
    	ip, port = dcInfo[0], dcInfo[1]
        self.sendMsg = 'CLIREQ:'+dcId+','+str(noOfTickets)
        self.recvMsg = ''
        self.chunk_size = 4096
        self.logger = logging.getLogger('EchoClient')
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.debug('connecting to %s', (ip, port))
        self.connect((ip, port))
        return
        
    def handle_connect(self):
        self.logger.debug('handle_connect()')
    
    def handle_close(self):
        self.logger.debug('handle_close()')
        self.close()
        #self.logger.debug('Received Data: '+ self.recvMsg)
        return
    
    def writable(self):
        self.logger.debug('writable() -> %s', bool(self.sendMsg))
        return bool(self.sendMsg)

    def handle_write(self):
        self.send(self.sendMsg)
        self.logger.debug('handle_write() -> "%s"', self.sendMsg)
        self.sendMsg = ''

    def handle_read(self):
        self.recvMsg = self.recv(self.chunk_size)
        self.logger.debug('handle_read() -> "%s"', self.recvMsg)
        self.handle_close()
        

c1 = Client()
#while True:
c1.buyTickets('dc1', ['127.0.0.1', 5001], 3)
asyncore.loop()
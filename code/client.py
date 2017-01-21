import socket
import time

class Client:
    def buyTickets(self, dcId, dcInfo, noOfTickets):

        ip, port = dcInfo[0], dcInfo[1]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        time.sleep(30)
        reqMsg = 'CLIREQ:'+dcId+','+str(noOfTickets)
        s.send(reqMsg)
        data = s.recv(4096)
        s.close()
        print('Received', repr(data))

c1 = Client()
c1.buyTickets('dc1', ['127.0.0.1', 5001], 3)
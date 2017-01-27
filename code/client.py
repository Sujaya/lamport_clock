import socket
import time
import asyncore
import logging
import json, sys
logging.basicConfig(filename='client.log',level=logging.DEBUG)

with open('server_config.json') as config_file:    
    config = json.load(config_file)


delay = int(sys.argv[1])
BUFFER_SIZE = 2000 
 
 
while True:
    dcId = raw_input("Enter DataCenter ID/ Enter 0 to exit.:")
    if dcId == '0':
        break
    elif dcId not in config["datacenters"]:
        print 'Invalid entry! Please enter a valid datacenter.'
        continue
    
    noOfTickets = raw_input("Enter no. of tickets: ")
    if noOfTickets == 0:
        print 'Invalid entry! Please enter a valid ticket count.'
        continue

    ip, port = config["datacenters"][dcId][0], config["datacenters"][dcId][1]
    reqMsg = 'CLIREQ::'+dcId+','+str(noOfTickets)+','+json.dumps({'seqNo':0})

    tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    time.sleep(delay)
    tcpClient.connect((ip, port))
    tcpClient.send(reqMsg)

    data = tcpClient.recv(BUFFER_SIZE)
    while not data:
        data = tcpClient.recv(BUFFER_SIZE)
    print data

    tcpClient.close() 


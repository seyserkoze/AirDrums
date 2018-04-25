import socket
import sys
from random import randint
import time


#to be modified: currently is random
def sendVals():

	x = randint(-30, 30)
	y = randint(-30, 30)
	z = randint(-30, 30)

	word = (str(x)+ ' '+ str(y)+ ' '+ str(z))

	return word

def drumVal():
	return str(randint(0,5))

#to be implemented
def dataReady():
	return 1

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('localhost', 50000))

print "Listening...\n"
s.listen(1)

conn, addr = s.accept()
print "accepted..\n"

while 1:
	data = conn.recv(4)

	#send data about vector information
	if (data == 'SEND'):
		print "sending to client...\n"

		if dataReady():
			conn.sendall(sendVals())
			time.sleep(1)

	#receiving data about drumlist from server
	elif (data == 'READ'):
		print "reading from client...\n"
		drumlist = conn.recv(1024)
		print "drumlist is " + drumlist

	#drum hit indicator
	elif (data == "DRUM"):
		d = drumVal()
		print "sending drum hit: " + d 
		conn.sendall(d)
		time.sleep(1)

	elif (data == "BACK"):
		print "backed out from sending client data values.."

	elif (data == 'SHUT'):
		print "shutting down.."
		conn.shutdown(socket.SHUT_RDWR)
		conn.close()
		exit()




import socket
from threading import Thread

class RemoteInputHandler:
	def __init__(self):
		self.drum_config = None
		self.accel = None
		self.last_drum = None
		self.end_program = False
		self.host = 'localhost'
		self.port = 50000
		self.drums_per_row = 3 

	# sends accel vals
	def sendVals(self):
		x,y,z = self.accel if self.accel is not None else [0,0,0]
		word = (str(x) + ' ' + str(y) + ' ' + str(z))
		return word

	# return last drum hit
	def drumVal(self):
		return str(self.last_drum) if self.last_drum is not None else str(-1)


	def thread_fn(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		drumsLength = 17
		sock.bind((self.host, self.port))
		print "Listening...\n"
		sock.listen(1)

		conn, addr = sock.accept()
		print "accepted..\n"

		while True:
			data = conn.recv(4)
			print 'here'
			#send data about vector information
			if (data == 'TEST'):
				print "sending to client...\n", self.sendVals()
				conn.sendall(self.sendVals())
				# time.sleep(1)

			#receiving data about drumlist from server
			elif (data == 'READ'):
				print "reading from client...\n"
				drumlist = conn.recv(drumsLength)
				print "Received drum list: ", drumlist
				self.drum_config = self.parseDrumVals(drumlist.split())

				print "list of drums is " + str(self.drum_config)

			#drum hit indicator
			elif (data == "DRUM"):
				d = self.drumVal()
				print "sending drum hit: " + d 
				conn.sendall(d)

			elif (data == "BACK"):
				print "backed out from sending client data values.."
				# conn.sendall("") # 

			elif (data == 'SHUT'):
				print "shutting down.."
				conn.shutdown(socket.SHUT_RDWR)
				conn.close()
				self.end_program = True
				break


	def update_accel(self, accels):
		self.accel = accels

	# x_pos and y_pos define a position in the drum 2D array
	def update_last_drum(self, x_pos, y_pos):
		self.last_drum = (y_pos * self.drums_per_row) + x_pos

	def get_drum_config(self):
		return self.drum_config

	def received_quit(self):
		return self.end_program

	def start(self):
		t = Thread(target=self.thread_fn)
		t.start()
		t.join()

	def parseDrumVals(self, drumConfig):

		finalresult = [None for i in xrange(6)]
		parseDict = {'sn' : 'snare', 'cr': 'crash', 'hh': 'hihats', 'ht': 'hitoms', 'lt': 'lotoms', 'ri': 'ride', 'em': 'empty'}

		for i in xrange(len(drumConfig)):
			finalresult[i] = parseDict[drumConfig[i]]

		return finalresult




r = RemoteInputHandler()
r.start()
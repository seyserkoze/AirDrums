
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
		self.quit = False

	# sends accel vals
	def sendVals(self):
		x,y,z = self.accel if self.accel is not None else [0,0,0]
		word = (str(x) + ' ' + str(y) + ' ' + str(z))
		return word

	# return last drum hit
	def drumVal(self):
		return str(self.last_drum) if self.last_drum is not None else str(-1)


	"""
	sn= snare, ri = ride, hh= hihats, ht = hitoms, lt = lotoms, cr = crash
	"""
	def drum_name(self, abbrev):
		name = ""
		mappings = {'sn':'snare', 'ri':'ride', 'hh':'hihats', 
		'ht':'hitoms', 'lt':'lotoms', 'cr':'crash', "em":"empty"}
		return mappings[abbrev] if abbrev in mappings else "empty"


	def thread_fn(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind((self.host, self.port))
		print "Listening...\n"
		sock.listen(1)

		conn, addr = sock.accept()
		print "accepted..\n"

		while not self.quit:
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
				drumlist_len = 17
				drumlist = conn.recv(drumlist_len)
				print "Received drum list: ", drumlist
				drumlist = drumlist.split()
				self.drum_config = [self.drum_name for d in drumlist]

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

	def force_quit(self):
		self.quit = True

	def start(self):
		t = Thread(target=self.thread_fn)
		t.start()


# r = RemoteInputHandler()
# r.start()

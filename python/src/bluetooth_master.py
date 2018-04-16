import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART, DeviceInformation
import time
import atexit
from uuid import UUID
import thread
import numpy as np
import matplotlib.pyplot as plt
import queue
from audio import Audio

# ---------------------------GLOBALS-----------------------------
end_program = False
# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()
sensor_data = []


#-----------------------Examples------------------------------
# prints device info
def device_info():
    # Clear any cached data because both bluez and CoreBluetooth have issues with
    # caching data and it going stale.
    ble.clear_cached_data()

    # Get the first available BLE network adapter and make sure it's powered on.
    adapter = ble.get_default_adapter()
    adapter.power_on()
    print('Using adapter: {0}'.format(adapter.name))

    # Disconnect any currently connected UART devices.  Good for cleaning up and
    # starting from a fresh state.
    print('Disconnecting any connected UART devices...')
    UART.disconnect_devices()

    # Scan for UART devices.
    print('Searching for UART device...')
    try:
        adapter.start_scan()
        # Search for the first UART device found (will time out after 60 seconds
        # but you can specify an optional timeout_sec parameter to change it).
        device = UART.find_device()
        if device is None:
            raise RuntimeError('Failed to find UART device!')
    finally:
        # Make sure scanning is stopped before exiting.
        adapter.stop_scan()

    print('Connecting to device...')
    device.connect()  # Will time out after 60 seconds, specify timeout_sec parameter
                      # to change the timeout.

    # Once connected do everything else in a try/finally to make sure the device
    # is disconnected when done.
    try:
        # Wait for service discovery to complete for the DIS service.  Will
        # time out after 60 seconds (specify timeout_sec parameter to override).
        print('Discovering services...')
        DeviceInformation.discover(device)

        # Once service discovery is complete create an instance of the service
        # and start interacting with it.
        dis = DeviceInformation(device)

        # Print out the DIS characteristics.
        print('Manufacturer: {0}'.format(dis.manufacturer))
        print('Model: {0}'.format(dis.model))
        print('Serial: {0}'.format(dis.serial))
        print('Hardware Revision: {0}'.format(dis.hw_revision))
        print('Software Revision: {0}'.format(dis.sw_revision))
        print('Firmware Revision: {0}'.format(dis.fw_revision))
        print('System ID: {0}'.format(dis.system_id))
        print('Regulatory Cert: {0}'.format(dis.regulatory_cert))
        print('PnP ID: {0}'.format(dis.pnp_id))
    finally:
        # Make sure device is disconnected on exit.
        device.disconnect()



# Main function implements the program logic so it can run in a background
# thread.  Most platforms require the main thread to handle GUI events and other
# asyncronous events like BLE actions.  All of the threading logic is taken care
# of automatically though and you just need to provide a main function that uses
# the BLE provider.
def uart_service():
	# Clear any cached data because both bluez and CoreBluetooth have issues with
	# caching data and it going stale.
	ble.clear_cached_data()

	# Get the first available BLE network adapter and make sure it's powered on.
	adapter = ble.get_default_adapter()
	adapter.power_on()
	print('Using adapter: {0}'.format(adapter.name))

	# Disconnect any currently connected UART devices.  Good for cleaning up and
	# starting from a fresh state.
	print('Disconnecting any connected UART devices...')
	UART.disconnect_devices()

	# Scan for UART devices.
	print('Searching for UART device...')
	try:
	    adapter.start_scan()
	    # Search for the first UART device found (will time out after 60 seconds
	    # but you can specify an optional timeout_sec parameter to change it).
	    device = UART.find_device()
	    if device is None:
	        raise RuntimeError('Failed to find UART device!')
	finally:
	    # Make sure scanning is stopped before exiting.
	    adapter.stop_scan()

	print('Connecting to device...')
	device.connect()  # Will time out after 60 seconds, specify timeout_sec parameter
	                  # to change the timeout.

    # Once connected do everything else in a try/finally to make sure the device
    # is disconnected when done.
	try:
	    # Wait for service discovery to complete for the UART service.  Will
	    # time out after 60 seconds (specify timeout_sec parameter to override).
	    print('Discovering services...')
	    UART.discover(device)
	    DeviceInformation.discover(device)

	    # Once service discovery is complete create an instance of the service
	    # and start interacting with it.
	    uart = UART(device)
	    dis = DeviceInformation(device)

	    print("Conntected to device: name: {}, id: {}".format(device.name, device.id))

	    # Write a string to the TX characteristic.
	    uart.write('Hello world!\r\n')
	    print("Sent 'Hello world!' to the device.")

	    # Now wait up to one minute to receive data from the device.
	    print('Waiting up to 60 seconds to receive data from the device...')
	    while(True):
	        received = uart.read(timeout_sec=40)
	        if received is not None:
	            # Received data, print it out.
	            print('Received: {0}'.format(received))
	        else:
	            # Timeout waiting for data, None is returned.
	            print('Received no data!')
	finally:
		print "Interrupted"
		device.disconnect() 




#-----------------------------MAIN Code-----------------------------


class Vector3D():
	def __init__(self, x, y,z):
		self.x = x
		self.y = y
		self.z = z

	def __str__(self):
		return "x: {} y: {} z: {}".format(self.x,self.y,self.z)

	def toArray(self):
		return np.array([self.x, self.y, self.z]) 


class AccelTracker():
	def __init__(self):
		self.displacement = np.array([0.0,0.0,0.0])
		self.velocity = np.array([0.0,0.0,0.0])
		self.acceleration_raw = np.array([0.0,0.0,0.0]) # unprocessed. raw sensor values
		self.acceleration = np.array([0.0,0.0,0.0]) # acceleration 
		self.accel_offsets = np.array([0.0103, 0.0167, -0.0213]) # arbitrary offsets based on sensor values
		# self.millis = lambda : int((time.time()) * 1000)
		self.just_started = False 


	#----------------Update algorithms----------------

	# takes in a vector3D of acceleration values. Accel input must be in SI units
	# assuems constant acceleration
	# assumes constant acceleration between updates
	# delta_t_ms is time diff between 2 readings in seconds
	def updateConstAccel(self, delta_t , accel_vect):
		elapsed_time = delta_t
		# print "t = {}".format(elapsed_time)
		self.curr_time = time.time() # update curr time after end of computation
		new_accel = np.array(accel_vect.toArray()) + self.accel_offsets
		# print new_accel
		# u should be last know velocity. a is the current accel = new_accel
		self.displacement = self.displacement + ((elapsed_time * self.velocity)  + (0.5 * (elapsed_time**2) * new_accel)) # s1 = s0 + u0t + 0.5(a1)t^2
		self.velocity = self.velocity + (elapsed_time * new_accel) # u1 = u0 + (a1)t
		self.acceleration = new_accel


	# takes in delta_t and accel_vect in SI units. Assumes accel changes linearly (constant grad)
	# does not apply offset all accelerations derived from deltas
	# mutates displacement, velocity and acceleration fields
	def updateLinearAccel(self, delta_t, accel_vect):
		accel_raw_new = np.array(accel_vect.toArray())
		accel_grad = (accel_raw_new - self.acceleration_raw) / float(delta_t) # this operation reduces error by doing differentials
		# calculate and update values of current state in dependency order
		self.displacement += (self.velocity * delta_t) + ((delta_t**2)*((1.0/6.0*accel_grad*delta_t) + (0.5*self.acceleration)))
		self.velocity += delta_t * ((0.5 * accel_grad * delta_t) + self.acceleration)
		self.acceleration = self.acceleration + (delta_t * accel_grad) # new accel using defined using diff values
		# print "Diff Accel = {}".format(self.acceleration)
		self.acceleration_raw = accel_raw_new

	#--------------API calls for class below------------

	# call to start or restart the tracker
	def start(self):
		self.displacement = np.array([0.0,0.0,0.0])
		self.velocity = np.array([0.0,0.0,0.0])
		self.acceleration = np.array([0.0,0.0,0.0])
		self.acceleration_diff = np.array([0.0,0.0,0.0])
		self.just_started = True

	# standardized interface api function to be used externally to update accelration
	# behaves according to the update algorithm used
	def updateAccel(self, delta_t, accel_vect):
		if self.just_started: # initialize  the first value for diff
			self.acceleration_raw = np.array(accel_vect.toArray())
			self.just_started = False
		else:
			self.updateLinearAccel(delta_t, accel_vect)
		sensor_data.append(self.acceleration)

	# gets diplacements. Returns a vector
	def getDisplacement(self):
		s = self.displacement
		return Vector3D(s[0], s[1], s[2]) 

	def getVelocity(self):
		v = self.velocity
		return Vector3D(v[0], v[1], v[2]) 

	def getAcceleration(self):
		a = self.acceleration
		return Vector3D(a[0], a[1], a[2]) 



class DrumPulseTracker():
	def __init__(self, amp_floor, amp_ceiling, pulse_window, name=""):
		"""
		analyse acceleration amplitude values for a single axis
		Pulse detected if a ceiling follows a floor within a pulse window
		amp_ceiling > floor
		"""
		self.amp_ceiling = amp_ceiling
		self.amp_floor = amp_floor
		self.pulse_window = pulse_window
		self.name = name
		
		# vars for pattern recognition
		self.last_accel = None
		# foor and ceil detected used to denot a particular state
		self.floor_detected = False
		self.ceiling_detected = False
		self.time_since_start = 0 # how many time units away the last pulse start was
		self.min_amp = float('inf')
		self.max_amp = float('-inf')
		self.pulse_id = 0
		self.pulse_amp = 0 # max pk-pk amp of pulse denoted by pulse id

	#----------------Internal helper functions----------

	def _addAccelSimple(self, accel_amp):
		# if accel is under floor
		if accel_amp <= self.amp_floor:
			self.floor_detected = True
			self.last_floor_time = 0
		else:
			if self.last_floor_time > self.pulse_window: 
				# reset floor detection variable
				self.floor_detected = False
				self.last_floor_time = 0
			else: # increment time ago last floor was
				self.last_floor_time += 1

		# if floor already detected and ceiling threshold crossed. 
		# Since floor detected, last_floor_time < pulse window
		if self.floor_detected and accel_amp >= self.amp_ceiling:
			self.pulse_detected = True
			# reset state variables
			self.floor_detected = False
			self.last_floor_time = 0 

	def _pulseStart(self, accel_amp):
		"""
		called to start a pulse check. Changes state variables to change to
		pulseMid stage if accel_amp <= floor
		floor and ceiling detected must be false when func is called
		"""
		if accel_amp > self.amp_floor:
			return # do nothing as start conditions not met 
		self.floor_detected = True
		self.min_amp = accel_amp # set the minimum amp for this pulse
		self.max_amp = accel_amp
		self.time_since_start = 0

	def _pulseRestart(self, accel_amp):
		"""
		Resets state variables and checks for start of pulse using accel_amp
		"""
		self.floor_detected = False
		self.ceiling_detected = False
		self._pulseStart(accel_amp) # check for pulse start


	def _pulseMain(self, accel_amp):
		"""
		called after a floor initiating a pulse is detected
		floor detected must be true
		"""
		# print self.time_since_start, self.min_amp, self.max_amp
		if self.time_since_start >= self.pulse_window:
			# not a pulse as took too long to complete. Reset state
			self._pulseRestart(accel_amp)
		else: # continue checks
			self.min_amp = min(accel_amp, self.min_amp)
			self.max_amp = max(accel_amp, self.max_amp)
			if self.ceiling_detected: # last accel was above ceiling
				if accel_amp < self.amp_ceiling:
					# end of pulse detected, update pulse id of and amp of new pulse
					self.pulse_id += 1
					self.pulse_amp = self.max_amp - self.min_amp # pk-pk amp
					# reset state
					self._pulseRestart(accel_amp)
					return
				else: # end not detected yet
					self.time_since_start += 1
			else: # still waiting for ceiling to be breached
				if accel_amp >= self.amp_ceiling:
					self.ceiling_detected = True
				self.time_since_start += 1


	# register Accel in system
	def _addAccel(self, accel_amp):
		# case on system modes
		if not self.floor_detected:
			self._pulseStart(accel_amp)
		else: # a pulse is in progress
			self._pulseMain(accel_amp)


	# -----------------Interface functions---------------
	# call to start or restart. Must always call before first update
	def start(self):
		self.last_accel = None
		# pulse_id not required to be reset
		self.min_floor = float('inf')
		self.max_ceil = float('-inf')
		self.pulse_amp = 0
		self.tick_counter = 0
		self.pulse_id = 0 

	# take in time between 2 readings and the acceleration for a single axis
	def update(self, t, accel_amp):
		"""
		returns pulse_id of the last detected pulse
		"""
		self.last_accel = accel_amp
		self._addAccel(accel_amp)
		return None if self.pulse_id == 0 else self.pulse_id

	def getAcceleration(self):
		return self.last_accel 

	def getPulseID(self):
		"""
		returns pulse id of last detected pulse. Returns None if no pulse detected yet
		"""
		return None if self.pulse_id == 0 else self.pulse_id

	def getPulseAmp(self):
		"""
		returns pk-pk amplitude of pulse corresponding to the pulse id, None if no pulse detected
		"""
		return None if self.pulse_id == 0 else self.pulse_amp


class PositionalTracker():
	"""
	Used to track positions on a single axis. Positions are represented
	by integers within [lo,,hi]. Current state is at start and start is in 
	[lo, hi]
	"""
	def __init__(self, start, lo, hi):
		self.lo = lo
		self.hi = hi
		self.__current_pos = start

	def _movedForward(self, t, accel):
		"""
		Called on every update with given update args
		returns True if object moved Forward False other wise
		"""
		raise NotImplementedError

	def _movedBackward(self, t, accel):
		"""
		Called on every update with given update args
		returns True if object moved back False otherwise
		"""
		raise NotImplementedError

	def start(self):
		raise NotImplementedError

	def update(self, t, accel):
		self.__current_pos += self._movedForward(t, accel) - self._movedBackward(t, accel)
		self.__current_pos = max(self.lo, min(self.__current_pos, self.hi))

	def getPosition(self):
		return self.__current_pos


class XPositionalTracker(PositionalTracker):
	def __init__(self, start, lo, hi):
		PositionalTracker.__init__(self, start,lo,hi)
		pulse_window = 6
		x_floor = -8.0
		x_ceil = 8.0 
		self.leftPulseTracker = DrumPulseTracker(x_floor, x_ceil, pulse_window, name="x_left")
		self.rightPulseTracker = DrumPulseTracker(x_floor, x_ceil, pulse_window, name="x_right")
		self.double_move = 70
	
	def start(self):
		self.leftPulseTracker.start()
		self.rightPulseTracker.start()


	def _sizeOfMove(self, max_amp):
		if abs(max_amp) > self.double_move:
			return 2
		else:
			return 1


	def _movedForward(self, t, accel):
		"""
		Returns size of move in the right direction
		"""	
		old_pulse = self.rightPulseTracker.getPulseID()
		if self.rightPulseTracker.update(t, accel) != old_pulse:
			return self._sizeOfMove(self.rightPulseTracker.getPulseAmp())
		return 0

	def _movedBackward(self,t, accel):
		"""
		Returns size of move in the left direction
		"""	
		# negate the acceleration values as a ceiling is detected first in a left move
		old_pulse = self.leftPulseTracker.getPulseID()
		if self.leftPulseTracker.update(t,-accel) != old_pulse:
			return self._sizeOfMove(self.leftPulseTracker.getPulseAmp())
		return 0


class YPositionalTracker(PositionalTracker):
	def __init__(self, start, lo, hi):
		PositionalTracker.__init__(self, start,lo,hi)
		pulse_window = 6
		y_floor = -8.0
		y_ceil = 8.0 
		self.upPulseTracker = DrumPulseTracker(y_floor, y_ceil, pulse_window, name="y_left")
		self.downPulseTracker = DrumPulseTracker(y_floor, y_ceil, pulse_window, name="y_right")
		self.double_move = 60
	
	def start(self):
		self.upPulseTracker.start()
		self.downPulseTracker.start()


	def _sizeOfMove(self, max_amp):
		if abs(max_amp) > self.double_move:
			return 2
		else:
			return 1


	def _movedForward(self, t, accel):
		"""
		Returns size of move in the up direction
		"""	
		old_pulse = self.upPulseTracker.getPulseID()
		if self.upPulseTracker.update(t, accel) != old_pulse:
			return self._sizeOfMove(self.upPulseTracker.getPulseAmp())
		return 0

	def _movedBackward(self,t, accel):
		"""
		Returns size of move in the down direction
		"""	
		# negate the acceleration values as a ceiling is detected first in a left move
		old_pulse = self.downPulseTracker.getPulseID()
		if self.downPulseTracker.update(t,-accel) != old_pulse:
			return self._sizeOfMove(self.downPulseTracker.getPulseAmp())
		return 0




class PeriodicPrinter():
	# period is seconds
	def __init__(self, period):
		self.period = period
		self.curr_time = time.time()

	def printVal(self, val):
		t = time.time()
		if t - self.curr_time > self.period:
			print val
			self.curr_time = t




# returns the devices in device_ids as a dictionary of id: device
def getDevices(device_ids, timeout=20):
	# Get the first available BLE network adapter and make sure it's powered on.
    adapter = ble.get_default_adapter()
    adapter.power_on()
    print('Using adapter: {0}'.format(adapter.name))

    # Disconnect any currently connected UART devices.  Good for cleaning up and
    # starting from a fresh state.
    print('Disconnecting any connected UART devices...')
    UART.disconnect_devices()

    # Scan for UART devices.
    print('Searching for UART device...')
    to_find = set(device_ids)
    found = set()
    try:
        adapter.start_scan()
        time_elapsed = 0
        while(time_elapsed < timeout and len(found) < len(device_ids)):
        	devices = UART.find_devices()
        	for d in devices:
        		# d.id is a UUID object
        		if d.id in to_find: #check if id in id_set
        			found.add(d) # add device to found
        	time.sleep(1.0)
        	time_elapsed += 1
        for device in found:
        	device.connect()
        	print("Discovering UART service for {}".format(device.id))
        	UART.discover(device)
    except:
    	for device in found:
    		# Make sure device is disconnected 
    		device.disconnect()
    	raise RuntimeError('Error Connecting to devices. Terminating ...')
    finally:
        # Make sure scanning is stopped before exiting.
        adapter.stop_scan()
   	return {device.id: device for device in found}

class UARTStream():
	def __init__(self, device, uart):
		self.device = device
		self.uart = uart
		self.read_remainder = ""

	# returns the last n bytes read. Blocks until n bytes read
	def readNBytes(self, n):
		bytes_read = len(self.read_remainder)
		timeout = 60
		str_arr = [self.read_remainder] if bytes_read > 0 else [] # holds all read strings
		while bytes_read < n:
			received = self.uart.read(timeout_sec=timeout)
			if received is not None:
				str_arr.append(received)
				bytes_read += len(received) # increment num bytes read
		self.read_remainder = "".join(str_arr)
		ret = self.read_remainder[0:n]
		self.read_remainder = self.read_remainder[n:]
		return ret

	# read until next limiter lim and returns string including lim. 
	# Blocks until first lim encountered
	def readUntil(self, lim):
		timeout = 60
		str_arr = [self.read_remainder]
		while True:
			received = self.uart.read(timeout_sec= timeout)
			if received is not None:
				str_arr.append(received)
				if lim in received:
					break
		self.read_remainder = "".join(str_arr)
		ret = self.read_remainder[0:self.read_remainder.find(lim)+1]
		self.read_remainder = self.read_remainder[self.read_remainder.find(lim)+1:]
		return ret

	def readBetween(self, start_char, end_char):
		self.readUntil(start_char)
		return "{}{}".format(start_char, self.readUntil(end_char))
		
	def write(self, write_str):
		self.uart.write(write_str)

# assumes data_str = '[x,y,z]'
# return (t in seconds, np.array[x,y,z]) 
def parseSensorData(data_str):
	vals = eval(data_str)

	if len(vals) != 4:
		assert False, "Parsed Bad Sensor Data"
	t = vals[0] # time in milliseconds
	return (t / 1000.0, np.array([vals[1],vals[2], vals[3]]))



def userInputHandler():
	print "Starting input handler"
	global end_program
	while 1:
		cmd = raw_input()
		if cmd == 'q': #quit program
			end_program = True
			return
	return 


def collectData(x_data, y_data, z_data):
	sensor_data.append([x_data, y_data, z_data])


# sensor_data is a 2d array. saves to file defined in function
def saveData(sensor_data):
	filename = "./sensor_data.csv"
	np.savetxt(filename, sensor_data, delimiter=",")


# polls sensors and starts user input handler thread
def start_system():
	global sensor_data
	allowed_ids = [UUID("1c7c996c-79b0-47df-905a-93233d6fdc67")]
	devices = getDevices(allowed_ids) # dict of uuid: device
	# uarts are used to read and write data over bluetooth
	uarts = {device.id: UART(device) for device in devices.values()}
	packet_len = 20

	uart_stream = UARTStream(devices[allowed_ids[0]], uarts[allowed_ids[0]])
	# tracker = AccelTracker()
	x_tracker = XPositionalTracker(0, -1, 1)
	y_tracker = YPositionalTracker(0, -1, 1)
	z_tracker = DrumPulseTracker(-10.0, 6.0, 6, name="z")
	accel_printer = PeriodicPrinter(1.0)
	try:
		thread.start_new_thread(userInputHandler, ())
		audio_player = Audio(5)
		accel_diff = np.array([0.0,0.0,0.0]) # assume starts from 0 
		accel_raw = None
		z_id = None
		
		# init trackers
		# x_tracker.start()
		# y_tracker.start()
		z_tracker.start()
		while not end_program:
			sensor_str = uart_stream.readBetween("[","]")
			# print "Received: {}".format(sensor_str)
			(t,accel_new) = parseSensorData(sensor_str)

			# perform differencing logic to remove systematic errors
			if accel_raw is None: # first sensor reading
				accel_raw = accel_new
				continue # skip this iteration
			else: # perform differencing on readings to remove systematic errors
				accel_grad = (accel_new - accel_raw) / t
				accel_raw = accel_new # update accel_raw value to current reading
				accel_diff += (accel_grad * t) # update accel_diff

			x,y,z = accel_diff
			x_tracker.update(t, x)
			y_tracker.update(t, y)
			if z_tracker.update(t, z) != z_id:
				z_id = z_tracker.getPulseID()
				print "Z Pulse Detected", z_tracker.getPulseID(), z_tracker.getPulseAmp() 
				print "X pos ", x_tracker.getPosition()
				print "Y pos", y_tracker.getPosition()
				audio_player.queue_sound("kick", 100)
			collectData(x,y,z)
			# sensor_data.append(vect.toArray())
			# accel_printer.printVal("Displacement = {}".format(tracker.getDisplacement()))
	#except Exception as e:
	#	print(e)
	#	raise e
	finally:
		for device in devices.values():
			device.disconnect()
		# plotSensorData(sensor_data)
		saveData(sensor_data)


#-----------------------------Execution-----------------------------

def main():
	# Clear any cached data because both bluez and CoreBluetooth have issues with
    # caching data and it going stale.
	ble.clear_cached_data()
	# call desired function here
	start_system()
	return


def run():
	# Initialize the BLE system.  MUST be called before other BLE calls!
	ble.initialize()

	# Start the mainloop to process BLE events, and run the provided function in
	# a background thread.  When the provided main function stops running, returns
	# an integer status code, or throws an error the program will exit.
	ble.run_mainloop_with(main)


run()
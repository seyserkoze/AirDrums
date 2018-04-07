import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART, DeviceInformation
import time
import atexit
from uuid import UUID
import thread
import numpy as np
import matplotlib.pyplot as plt

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
		return [self.x, self.y, self.z]


class AccelTracker():
	def __init__(self):
		self.displacement = np.array([0.0,0.0,0.0])
		self.velocity = np.array([0.0,0.0,0.0])
		self.acceleration = np.array([0.0,0.0,0.0])
		self.curr_time = 0 # in seconds
		self.accel_offsets = np.array([0.03, 0.0, 0.3]) # arbitrary offsets based on sensor values
		# self.millis = lambda : int((time.time()) * 1000)

	def start(self):
		self.displacement = np.array([0.0,0.0,0.0])
		self.velocity = np.array([0.0,0.0,0.0])
		self.acceleration = np.array([0.0,0.0,0.0])
		self.curr_time =  time.time() # self.millis()

	# takes in a vector3D of acceleration values. # input must be in SI units
	# assumes constant acceleration between updates
	def updateAccel(self, accel_vect):
		elapsed_time = float((time.time()) - self.curr_time) # in seconds
		self.curr_time = time.time() # update curr time after end of computation
		new_accel = np.array(accel_vect.toArray()) + self.accel_offsets
		print new_accel
		# u should be last know velocity. a is the current accel = new_accel
		self.displacement = self.displacement + ((elapsed_time * self.velocity)  + (0.5 * (elapsed_time**2) * new_accel)) # s1 = s0 + u0t + 0.5(a1)t^2
		self.velocity = self.velocity + (elapsed_time * new_accel) # u1 = u0 + (a1)t
		self.acceleration = new_accel 


	# gets diplacements. Returns a vector
	def getDisplacement(self):
		s = self.displacement
		return Vector3D(s[0], s[1], s[2]) 

	def getVelocity(self):
		v = self.velocity
		return Vector3D(v[0], v[1], v[2]) 


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
def parseSensorData(data_str):
	vals = eval(data_str)
	if len(vals) != 3:
		assert False, "Parsed Bad Sensor Data"
	vect = Vector3D(vals[0],vals[1], vals[2])
	return vect



def userInputHandler():
	print "Starting input handler"
	global end_program
	while 1:
		cmd = raw_input()
		if cmd == 'q': #quit program
			end_program = True
			return
	return 


def plotSensorData(sensor_data):
	# x_hist = np.histogram(sensor_data[:,0])
	print "Plotting..."
	sensor_data = np.array(sensor_data)
	data = sensor_data[:,0]
	plt.hist(data, bins=np.arange(data.min(), data.max()+1))
	plt.show()


# sensor_data is a 2d array. saves to file defined in function
def saveData(sensor_data):
	filename = "./sensor_data.csv"
	np.savetxt(filename, sensor_data, delimiter=",")

def loadData():
	filename = "./sensor_data.csv"
	return np.loadtxt(filename, delimiter=",")


# polls sensors and starts user input handler thread
def start_system():
	global sensor_data
	allowed_ids = [UUID("1c7c996c-79b0-47df-905a-93233d6fdc67")]
	devices = getDevices(allowed_ids) # dict of uuid: device
	# uarts are used to read and write data over bluetooth
	uarts = {device.id: UART(device) for device in devices.values()}
	packet_len = 20

	uart_stream = UARTStream(devices[allowed_ids[0]], uarts[allowed_ids[0]])
	tracker = AccelTracker()
	accel_printer = PeriodicPrinter(1.0)
	try:
		thread.start_new_thread(userInputHandler, ())
		tracker.start()
		while not end_program:
			sensor_str = uart_stream.readBetween("[","]")
			# print "Received: {}".format(sensor_str)
			vect = parseSensorData(sensor_str)
			sensor_data.append(vect.toArray())
			tracker.updateAccel(vect)
			accel_printer.printVal("Displacement = {}".format(tracker.getDisplacement()))
			# print "velocity: {}".format(tracker.getVelocity().toArray())

	# except Exception as e:
	#	print(e)
#		raise e
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

import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART, DeviceInformation
import time
import atexit
from uuid import UUID
import thread
import numpy as np
from audio import Audio
from trackers import DrumPulseTracker, XPositionalTracker, YPositionalTracker

# ---------------------------GLOBALS-----------------------------
end_program = False
# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()
sensor_data = []
drum_config = [["snare", "lotoms", "crash"],
				["ride", "kick", "hihats"]]

#----------------------Debugging functions---------------------

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

def collectData(x_data, y_data, z_data):
	sensor_data.append([x_data, y_data, z_data])


# sensor_data is a 2d array. saves to file defined in function
def saveData(sensor_data):
	filename = "./sensor_data.csv"
	np.savetxt(filename, sensor_data, delimiter=",")


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


class DrumSoundMapper:
	"""
	Takes in a drums array, volume_range tuple and accel_range tuple
	Generates a sound data tuple (drum_name, attack) for entry into audio
	player
	drums_arr should be of shape d_row * d_cols. Front drum is at position [1, 1]
	and is treated as being at coordinates [0,0]

	"""
	
	def __init__(self, drums_arr, accel_range):
		# constant parameters
		self.d_rows = 2
		self.d_cols = 3
		self.max_attack = 7

		self.drums_arr = np.array(drums_arr).reshape((self.d_rows, self.d_cols))
		self.accel_range = accel_range


	def _attackValue(self, accel):
		"""
		Given and acceleration value, return an attack value [0,max_attack]
		"""
		accel = int(self.max_attack * (accel - self.accel_range[0]) /(self.accel_range[1] - self.accel_range[0]))
		return max(0, min(accel, self.max_attack))

	def _drumType(self, x_pos, y_pos):
		"""
		Return the correct drum type based on drum configuration defined by drums_arr and assumption
		of a 2 x 3 drum grid
		"""
		start_x = 1
		start_y = 1
		return self.drums_arr[start_y + y_pos][start_x + x_pos]


	def getDrumSound(self, x_pos, y_pos, accel):
		"""
		Given x_pos, y_pos and acceleration. x_pos and y_pos should be ints in 
		range [-1, 1] and [0,1] respectively
		"""
		return (self,_drumType(x_pos, y_pos), self._attackValues(accel))

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
	y_tracker = YPositionalTracker(0, 0, 1)
	z_tracker = DrumPulseTracker(-10.0, 6.0, 6, name="z")
	sound_mapper = DrumSoundMapper(drum_config, (0, 60))
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
				x_pos = x_tracker.getPosition()
				y_pos = y_tracker.getPosition()
				print "Z Pulse Detected", z_id, z_tracker.getPulseAmp() 
				print "X pos ", x_pos 
				print "Y pos", y_pos
				sound = sound_mapper.getDrumSound(z_tracker.getPulseAmp(),x_pos, y_pos)
				print "Playing: ", sound
				audio_player.queue_sound(sound)

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
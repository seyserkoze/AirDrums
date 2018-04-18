import numpy as np
import matplotlib.pyplot as plt
from trackers import *


def plotSensorData(sensor_data, col=0, binstep=0.1):
	# x_hist = np.histogram(sensor_data[:,0])
	print "Plotting..."
	assert (col < sensor_data.shape[1] and col >= 0), "Wrong col argument"
	data = sensor_data[:,col]
	print "Bin range = {},{},{}".format(data.min(), data.max(), binstep)
	plt.hist(data, bins=np.arange(data.min(), data.max()+binstep, binstep))
	plt.show()


def plotAllData(sensor_data, binsteps=[0.01,0.01,0.05]):
	print "Plotting all ..."
	titles = ["x-axis", "y-axis", "z-axis"]
	for col in xrange(sensor_data.shape[1]):
		data = sensor_data[:,col]
		plt.subplot(sensor_data.shape[1], 1, col+1)
		plt.hist(data, bins=np.arange(data.min(), data.max() + binsteps[col], binsteps[col]))
		plt.title(titles[col])
		print titles[col], " ave = {}".format(data.mean()), " sum = {}".format(data.sum())
	# plt.l(["x","y","z"])
	plt.show()

def plotAccelOverTime(sensor_data, col=0):
	plt.plot(sensor_data[:, 0])
	plt.show()


def plotAllAccelOverTime(sensor_data):
	print "plotting all accel ..."
	titles = ["x-axis", "y-axis", "z-axis"]
	for col in xrange(sensor_data.shape[1]):
		plt.subplot(sensor_data.shape[1], 1, col +1)
		plt.plot(sensor_data[:, col])
		plt.title(titles[col])
	plt.show() 


def simulatePos(sensor_data):
	xpt = XPositionalTracker(1,0,2)
	ypt = YPositionalTracker(1,0,1)
	zpt = DrumPulseTracker(-7.0, 8.0, 7, name="z")
	xpt.start()
	ypt.start()
	zpt.start()
	t = 0
	x_pos = []
	z_hit = []
	for (x,y,z) in sensor_data:
		xpt.update(t, x)
		ypt.update(t,y)
		zpt.update(t, z)
		x_pos.append(xpt.getPosition())
		z_hit.append(zpt.getPulseID())
		t += 1
	print x_pos
	# print [z if z is not None else 0 for z in z_hit]
	return 

filename = "./sensor_data.csv"
sensor_data = np.loadtxt(filename, delimiter=",")
# print sensor_data[20:30, :]
#plotSensorData(sensor_data, col=0, binstep=0.01)
#plotAccelOverTime(sensor_data, col=0)
#plotAllData(sensor_data)
# print sensor_data[45:68, 0]
simulatePos(sensor_data)
plotAllAccelOverTime(sensor_data)






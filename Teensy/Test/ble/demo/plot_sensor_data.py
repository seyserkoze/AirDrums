import numpy as np
import matplotlib.pyplot as plt


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
	# plt.l(["x","y","z"])
	plt.show()



filename = "./sensor_data.csv"
sensor_data = np.loadtxt(filename, delimiter=",")
# print sensor_data[20:30, :]
#plotSensorData(sensor_data, col=0, binstep=0.01)
plotAllData(sensor_data)
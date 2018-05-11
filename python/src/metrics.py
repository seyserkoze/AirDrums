
import numpy as np

def test_latency(actual_arr, expected_arr):
    """
    tests latency of drum hit algorithm
    :param actual_arr: array of actual values obtained from testing
    :param expected_arr: array of expected values input by tester
    :return: average latency
    """
    total = sum([(actual - expected) for (actual, expected) in zip(actual_arr, expected_arr)])
    num = len(actual_arr)
    return float(total/num)

def test_accuracy(actual_arr, expected_arr):
    """
    tests accuracy of drum hit algorithm
    :param actual_arr: array of actual values obtained from testing
    :param expected_arr: array of expected values input by tester
    :return: number of errors in run
    """
    num_errors = sum([1 for (actual, expected) in zip(actual_arr, expected_arr) if actual != expected])
    return num_errors


def getTimes():
    filename = "./time_data.csv"
    times = np.loadtxt(filename, delimiter=",")
    return times

def getHits():
    filename = "./hit_data.csv"
    return np.loadtxt(filename, delimiter=",")



"""
exp_hits = [4,4,4,4,3,4,5]
times = getTimes()[0:20]
print len(times), times[0:20] 
hits = getHits()[0:]
exp_hits = [4,4,3,4,5,2]
print test_latency(times[:,1], times[:,0])
print test_accuracy(exp_hits, hits)
"""



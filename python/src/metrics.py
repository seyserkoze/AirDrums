def test_latency(initial_time_arr, final_time_arr):
    """
    tests latency of drum hit algorithm
    :param initial_time_arr: array of initial values obtained from Arduino
    :param final_time_arr: array of final times input by tester
    :return: average latency
    """
    total = sum([(final - initial) for (final, initial) in zip(initial_time_arr, final_time_arr)])
    num = len(final_time_arr)
    return float(total/num)


def test_accuracy(actual_arr, expected_arr):
    """
    tests accuracy of drum hit algorithm
    :param actual_arr: array of actual values obtained from testing
    :param expected_arr: array of expected values input by tester
    :return: number of errors in run
    """
    num_errors = sum([1 for (actual, expected) in zip(actual_arr, expected_arr) if (actual != expected)])
    return num_errors

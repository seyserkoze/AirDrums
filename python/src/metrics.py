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

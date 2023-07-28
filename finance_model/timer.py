import functools
import time


def timer(function):
    """
    Record and print the execution time of a function.

    This function is to be used as a decorator to functions. It will record the time
    that the function starts and stops, and will print the total duration to STDOUT.

    :param function: The function to be timed.
    :return: the wrapper function
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        value = function(*args, **kwargs)
        end_time = time.perf_counter()
        duration = end_time - start_time
        print(f"Total duration for function <{function.__name__}> is {duration}")
        return value

    return wrapper


class Timer:
    def __init__(self, timer_name):
        self.timer_name = timer_name

    def __enter__(self):
        self.start_time = time.perf_counter()

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.end_time = time.perf_counter()
        duration = self.end_time - self.start_time
        print(f"Total duration for code segment <{self.timer_name}> is {duration}")

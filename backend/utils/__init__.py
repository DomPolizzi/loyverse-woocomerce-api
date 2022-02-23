import time
from .vars import *

def get_milli_time():
    """
    Function to get time in milliseconds

    :return: time in milliseconds
    """
    return time.time() * 1000

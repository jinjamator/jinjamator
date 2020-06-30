import time
import datetime


def today():
    """
    returns a timestamp of today
    """
    return time.mktime(datetime.date.today().timetuple())

import time
import struct

# Remove the extra bit that is sometimes set in a device ID and upcase the letters
def dev_id_str(dev_id):
    return ("%x" % (dev_id & 0xff7fffff)).upper()

# format a date
def format_datestamp(timestamp):
    return time.strftime("%Y-%m-%d", time.localtime(timestamp))

# format a time
def format_timestamp(timestamp):
    return time.strftime("%H:%M:%S", time.localtime(timestamp))

# format a timestamp using asctime
# return the hex value if timestamp is invalid
def format_datetime(timestamp):
    try:
        return time.asctime(time.localtime(timestamp))
    except ValueError:
        return ''.join(x.encode('hex') for x in struct.pack("<L", timestamp))

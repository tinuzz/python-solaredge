from .devicebase import Device

# https://github.com/jbuehl/solaredge/issues/47

class Event(Device):

    labels = [
        'Date', 'Time', 'Timestamp', 'Type', 'Param1',
        'Param2', 'Param3', 'Param4', 'Param5'
    ]
    fmt = '<LLLLLLL'
    item_idx = [ 0, 0, 0, 1, 2, 3, 4, 5, 6 ]

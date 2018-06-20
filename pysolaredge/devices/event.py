from .devicebase import Device

# https://github.com/jbuehl/solaredge/issues/47

class Event(Device):

    labels = [
        'date', 'time', 'timestamp', 'type', 'param1',
        'param2', 'param3', 'param4', 'param5'
    ]
    fmt = '<LLLLLLL'
    item_idx = [ 0, 0, 0, 1, 2, 3, 4, 5, 6 ]

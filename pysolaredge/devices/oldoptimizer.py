from .devicebase import Device

class Oldoptimizer(Device):

    labels = [
        'Date', 'Time', 'Inverter', 'Uptime', 'Vmod', 'Vopt', 'Imod', 'Eday', 'Temp'
    ]
    fmt = '<LLLLfffff'
    item_idx = [0, 0, 1, 3, 4, 5, 6, 7, 8]

from .devicebase import Device

class Meter(Device):

    labels = [
        'Date','Time', 'Timestamp', 'RecType', 'TotalE2Grid', 'TotalEfromGrid'
        'Interval', 'IntvE2Grid', 'IntvEfromGrid', 'P2Grid', 'PfromGrid'
    ]
    fmt = '<LBBLH2sLH2sLH2sLH2sLLLff'   # 20 items
    item_idx = [ 0, 0, 0, 1, 3, 6, 15, 16, 17, 18, 19 ]

    def post_process(self, parsed):
        # 'P from grid' should be 0 sometimes
        parsed[10] = 0 if parsed[10] < -3.4e+38 else parsed[10]
        return parsed

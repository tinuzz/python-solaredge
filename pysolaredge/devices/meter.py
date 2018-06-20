from .devicebase import Device

class Meter(Device):

    labels = [
        'date', 'time', 'timestamp', 'Rec_Type', 'e_exp_total', 'e_imp_total'
        'interval', 'e_exp_intv', 'e_imp_intv', 'p_exp', 'p_imp'
    ]
    fmt = '<LBBLH2sLH2sLH2sLH2sLLLff'   # 20 items
    item_idx = [ 0, 0, 0, 1, 3, 6, 15, 16, 17, 18, 19 ]

    def post_process(self, parsed):
        # 'P from grid' should be 0 sometimes
        parsed[10] = 0 if parsed[10] < -3.4e+38 else parsed[10]
        return parsed

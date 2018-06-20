from .devicebase import Device

class Inverter3ph(Device):

    # https://github.com/jbuehl/solaredge/blob/master/se/dataparams.py#L68

    labels = [
        'date', 'time', 'timestamp', 'uptime', 'interval', 'temperature', 'e_day', 'e_ac_intv', 'v_ac1',
        'v_ac2', 'v_ac3', 'i_ac1', 'i_ac2', 'i_ac3', 'frequency1', 'frequency2', 'frequency3',
        'e_day_dc', 'e_dc', 'v_dc', 'i_dc', 'e_total', 'i_rcd', 'data21', 'data22',
        'data23', 'cos_phi1', 'cos_phi2', 'cos_phi3', 'mode', 'gnd_fr_r', 'data29',
        'i_out_dc', 'data31', 'type'
    ]

    # Data should be 258 bytes
    fmt = '<LLLffffffffffffLLfLffLLLfffLfffL'
    item_idx = [
        0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
        21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31
    ]

    def post_process(self, parsed):
        parsed.append('3-phase')
        return parsed

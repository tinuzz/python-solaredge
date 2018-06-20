from .devicebase import Device

class Inverter1ph(Device):

    labels = [
        'date', 'time', 'timestamp', 'uptime', 'interval', 'temperature', 'e_day', 'e_ac_intv', 'v_ac',
        'i_ac', 'frequency', 'v_dc', 'i_dc', 'e_total', 'i_rcd',
        'cos_phi', 'mode', 'p_max', 'pf_pct', 'i_out_dc', 'p_active', 'p_apparent','p_reactive'
    ]

    fmt = "<LLLffffffffffffffLfffffffffffLL"
    item_idx = [0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 16, 17, 18, 19, 20, 23, 24, 25]

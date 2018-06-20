from .devicebase import Device

class Battery(Device):

    # Untested

    labels = [
        'date', 'time', 'timestamp', 'battery_id', 'v_dc', 'i_dc',
        'capacity_nom', 'capacity_actual', 'charge', 'e_in_total',
        'e_out_total', 'temperature', 'charging_status', 'interval', 'e_in_intv',
        'e_out_intv'
    ]
    fmt = 'L12sfffffLfLf4s4sfHffLLL'     # 20 items
    item_idx = [ 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 9, 13, 14, 17, 18, 19 ]

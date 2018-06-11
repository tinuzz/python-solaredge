from .devicebase import Device

class Battery(Device):

    # Untested

    labels = [
        'Date', 'Time', 'Timestamp', 'batteryId', 'Vdc', 'Idc',
        'BattCapacityNom', 'BattCapacityActual', 'BattCharge', 'TotalEnergyIn',
        'TotalEnergyOut', 'Temp', 'BattChargingStatus', 'Interval', 'IntvlEIn',
        'IntvlEOut'
    ]
    fmt = 'L12sfffffLfLf4s4sfHffLLL'     # 20 items
    item_idx = [ 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 9, 13, 14, 17, 18, 19 ]

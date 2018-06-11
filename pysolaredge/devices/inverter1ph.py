from .devicebase import Device

class Inverter1ph(Device):

    labels = [
        "Date", "Time", "Uptime", "Interval", "Temp", "Eday", "Eac", "Vac",
        "Iac", "Freq", "Vdc", "Etot", "Pmax", "Pac"
    ]

    # Inverter data should be 104 bytes long
    fmt = "<LLLffffffLLfLffLfffffLLffL"
    item_idx = [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 13, 18, 23]

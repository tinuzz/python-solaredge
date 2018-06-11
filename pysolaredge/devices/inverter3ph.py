from .devicebase import Device

class Inverter3ph(Device):

    # https://github.com/jbuehl/solaredge/blob/master/se/dataparams.py#L68

    labels = [
        "Date", "Time", "Uptime", "Interval", "Temp", "Eday", "Eac", "Vac1",
        "Vac2", "Vac3", "Iac1", "Iac2", "Iac3", "Freq1", "Freq2", "Freq3",
        "EdayDC", "Edc", "Vdc", "Idc", "Etot", "Irdc", "data21", "data22",
        "data23", "CosPhi1", "CosPhi2", "CosPhi3", "mode", "GndFrR", "data29",
        "IoutDC", "data31", "Type"
    ]

    # Data should be 258 bytes
    fmt = '<LLLffffffffffffLLfLffLLLfffLfffL'
    item_idx = [
        0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
        21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31
    ]

    def post_process(self, parsed):
        parsed.append('3-phase')
        return parsed

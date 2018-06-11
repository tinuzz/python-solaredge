from .devicebase import Device
import struct

class Optimizer(Device):

    labels = [
        'Date', 'Time', 'Timestamp', 'Uptime', 'Vmod', 'Vopt', 'Imod', 'Eday', 'Temp'
    ]

    def parse(self):

        # Optimizer data is 13 bytes:
        # - timestamp  : bytes 1-4, seconds since epoch
        # - uptime     : bytes 5-6, seconds
        # - Vpanel     : 10 bits, 1/8 V
        # - Voptimizer : 10 bits, 1/8 V
        # - Current    : 12 bits, 1/160 A
        # - Eday       : bytes 11-12, 1/4 Wh
        # - temperature: byte  13, (2 degC)  Signed?, 2.0 is best guess at factor

        data = self.data
        timestamp, uptime = struct.unpack('<LH', data[0:6])

        # 6        7        8        9
        # 00000011 11000001 00010011 00010101
        # --------       --
        v0 = struct.unpack('<H', data[6:8])[0]
        vpan = (v0 & 0x3ff) / 8
        #vpan = (int.from_bytes(data[6:8], byteorder='little') & 0x3ff) / 8

        # 00000011 11000001 00010011 00010101
        #          ------       ----
        v0 = struct.unpack('<H', data[7:9])[0]
        vopt = (v0 >> 2 & 0x3ff) / 8

        # 00000011 11000001 00010011 00010101
        #                   ----     --------
        v0 = struct.unpack('<H', data[8:10])[0]
        imod = (v0 >> 4 & 0x3ff) / 160

        eday = 0.25 * (data[11] << 8 | data[10])
        # TODO:
        #eday = struct.unpack('<H', data[10:12])[0] / 4
        #eday = int.from_bytes(data[10:12], byteorder='little') / 4

        temp = 2.0 * struct.unpack("<b", data[12:13])[0]
        # temp = int.from_bytes(data[12:13], byteorder='little', signed=True)

        # Don't have an inverter ID in the data, substitute 0
        parsed = [ timestamp, timestamp, timestamp, uptime, vpan, vopt, imod, eday, temp ]
        return self.device_data(parsed)

    # Instead of overriding parse(), we could also rely on the standard behaviour
    # and use post_process() to fix up the result. However, we would have to fix up
    # 6 out of 9 fields, and the code would be much uglyer and harder to understand.

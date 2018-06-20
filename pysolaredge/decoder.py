import struct
import binascii
import time
import logging
from . import crypto, utils
from .exceptions import SeError, CryptoNotReadyError
from . import devices

class Decoder(object):

    privkey = None
    last_503_msg = None
    magic = b'\x12\x34\x56\x79'
    magic_len = len(magic)
    header_len = 16
    checksum_len = 2
    crypto = None

    def __init__(self, privkey=None, last_503_msg=None):
        self.logger = logging.getLogger(__name__)
        self.set_privkey(privkey)
        self.set_last_503_msg(last_503_msg)

    def set_privkey(self, privkey):
        if len(privkey) == 32:
            privkey = binascii.unhexlify(privkey)
        self.privkey = privkey
        self.init_crypto()

    def set_last_503_msg(self, last_503_msg):
        self.last_503_msg = last_503_msg
        self.init_crypto()

    def init_crypto(self):
        if self.crypto is None:
            if self.privkey is not None and self.last_503_msg is not None:
                self.decode(self.last_503_msg)

    def decode(self, data):
        self.logger.info('Starting decode')
        self.reset_data(data)
        self.validate_data()
        decoded = None

        if self.function == 0x003d:
            if self.crypto is None:
                raise CryptoNotReadyError('Cannot decrypt: crypto not ready')

            # Encrypted message. Decrypt and recurse.
            self.reset_data(self.crypto.decrypt(self.payload))
            return self.decode(self.data)

        if self.function == 0x0500:
            # Telemetry message. Parse and return data.
            decoded = self.handle_500()

        if self.function == 0x0503:
            # Temporary key update. Parse and return data.
            decoded = self.handle_503()

        if self.function == 0x0080:
            self.logger.info('ACK message, seq: %d' % self.msg_seq)
            decoded = {}

        if self.function == 0x0090:
            self.logger.debug('Private key component: %s' % self.printable)
            decoded = {}

        if decoded is not None:
            return {
                'seq': self.msg_seq,
                'function': self.function,
                'src': self.from_addr,
                'dst': self.to_addr,
                'decoded': decoded,
            }
        else:
            self.logger.warning('Unknown function 0x%04x' % self.function)

    def reset_data(self, data=None):
        self.data = data
        self.printable = binascii.hexlify(data).decode('ascii')
        self.function = None
        self.payload = None

    def validate_data(self):
        # This method will update relevant attributes or raise an exception

        length0 = len(self.magic) + self.header_len
        length1 = length0 + self.checksum_len

        # A message should have the magic string, a header and a checksum at minimum
        if len(self.data) < length1:
            raise SeError('Message too short, should be %d bytes minimum: %s' % (length1,self.printable))

        # Parse the header (20 bytes total)
        (magic, data_len, data_len_inv, msg_seq, from_addr, to_addr, function) = struct.unpack("<4sHHHLLH", self.data[0:length0])

        # Check if the message has the magic word
        if magic != self.magic:
            raise SeError('Illegal message: magic word not found')

        length2 = length1 + data_len

        # Check message length
        if len(self.data) == length2:
            self.logger.info('Message length as expected: %d' % length2)
        else:
            self.logger.warning('Expected message length to be %d bytes, but got %d' % (length2, len(self.data)))

        self.function = function
        self.payload =  self.data[length0:length0 + data_len]
        self.msg_seq = msg_seq
        self.from_addr = from_addr
        self.to_addr = to_addr

        # Validate the checksum. If the message is truncated, the checksum
        # position will be out of range and a struct.error will be raised.
        try:
            checksum = struct.unpack("<H", self.data[length2-self.checksum_len:length2])[0]
        except struct.error as e:
            checksum = 0
        calcsum = self.calc_crc( struct.pack(">HLLH", msg_seq, from_addr, to_addr, function) + self.payload)

        if checksum == calcsum:
            self.logger.info('Checksum passed: 0x%04x' % checksum)
        else:
            self.logger.error('Checksum error: expected 0x%04x, message has 0x%04x' % (calcsum, checksum))

        self.logger.info('Validated message: seq=0x%04x (%d), from=0x%08x, to=0x%08x, function=0x%04x' %
            (msg_seq, msg_seq, from_addr, to_addr, function))

    def handle_500(self):
        self.logger.info('Handling 0x0500 message with %d bytes payload. Msg_seq = %d' %
            (len(self.payload), self.msg_seq))
        if len(self.payload) > 0:
            pdata = self.parse_0x0500_payload()
            return pdata
        else:
            self.logger.info('No 0x0500 payload found, nothing to do')

    def handle_503(self):
        # This method will reinitialize the decryptor if the private key is known
        # 503 payload should be 34 bytes
        self.logger.info('Handling 0x0503 message')

        if self.privkey is None:
            raise SeError('Cannot handle 0x0503 message: missing private key')

        self.crypto = crypto.Crypto(self.privkey,self.payload)

        # We must return *something*
        return { 'result': 'success' }

    def parse_0x0500_payload(self):
        data = self.payload
        inverters = {}
        inverters3ph = {}
        optimizers = {}
        meters = {}
        events = {}
        batteries = {}

        for dev_type, dev_id, chunk_len, chunk in self.get_0x0500_chunk():

            dev_type_str = self.get_dev_type_str(dev_type)
            self.logger.info('Data chunk found: type=0x%04x (%s data), dev_id=%s, len=%d' %
                (dev_type, dev_type_str, dev_id, chunk_len))

            if not self.check_data_len(chunk, chunk_len):
                continue

            if dev_type == 0x0000:
                dev = devices.Oldoptimizer(dev_id, chunk)
                optimizers[dev_id] = dev.parse()
            elif dev_type == 0x0080:
                dev = devices.Optimizer(dev_id, chunk)
                optimizers[dev_id] = dev.parse()
            elif dev_type == 0x0010:
                dev = devices.Inverter1ph(dev_id, chunk)
                inverters[dev_id] = dev.parse()
            elif dev_type == 0x0011:
                dev = devices.Inverter3ph(dev_id, chunk)
                inverters3ph[dev_id] = dev.parse()
            elif dev_type == 0x0300:
                dev = devices.Event(dev_id, chunk)
                events[dev_id] = dev.parse()
            elif dev_type == 0x0022:
                dev = devices.Meter(dev_id, chunk)
                meters[dev_id] = dev.parse()
            elif dev_type == 0x0030:
                dev = devices.Battery(dev_id, chunk)
                batteries[dev_id] = dev.parse()
            else:
                self.logger.warning('Cannot parse data type 0x%04x' % dev_type)

        result = {}
        result["inverters"] = inverters
        result["inverters3ph"] = inverters3ph
        result["optimizers"] = optimizers
        result["events"] = events
        result["meters"] = meters
        result["batteries"] = batteries
        return result

    # Read the payload of a 0x0500 message and yield a chunk per data item
    def get_0x0500_chunk(self):
        data = self.payload
        header_len = 8
        ptr = 0

        while ptr < len(data):
            # Read the header
            dev_type, dev_id, chunk_len = struct.unpack("<HLH", data[ptr:ptr + header_len])
            dev_id = utils.dev_id_str(dev_id)
            ptr += header_len
            chunk = data[ptr:ptr + chunk_len]
            ptr += chunk_len
            yield ( dev_type, dev_id, chunk_len, chunk )

    def check_data_len(self, data, length):
        if len(data) < length:
            self.logger.error('Expected %d bytes of data, but only got %d' % (length, len(data)))
            return False
        return True

    def get_dev_type_str(self, dev_type):
        dev_types = {
            0x0000: 'optimizer (old format)',
            0x0080: 'optimizer',
            0x0010: '1-phase inverter',
            0x0011: '3-phase inverter',
            0x0300: 'event',
            0x0022: 'meter',
            0x0030: 'battery',
            0x0017: 'unknown',
        }
        try:
            return dev_types[dev_type]
        except KeyError:
            return 'unknown'

    # CRC-16 with the following parameters:
    # width=16 poly=0x8005 init=0x5a5a refin=true refout=true xorout=0x0000

    def calc_crc(self, data):
        crc = 0x5a5a  # initial value
        for d in data:
            crc = self.crc_table[(crc ^ d) & 0xff] ^ (crc >> 8)
        return crc

    crc_table = [
        0x0000, 0xc0c1, 0xc181, 0x0140, 0xc301, 0x03c0, 0x0280, 0xc241, 0xc601,
        0x06c0, 0x0780, 0xc741, 0x0500, 0xc5c1, 0xc481, 0x0440, 0xcc01, 0x0cc0,
        0x0d80, 0xcd41, 0x0f00, 0xcfc1, 0xce81, 0x0e40, 0x0a00, 0xcac1, 0xcb81,
        0x0b40, 0xc901, 0x09c0, 0x0880, 0xc841, 0xd801, 0x18c0, 0x1980, 0xd941,
        0x1b00, 0xdbc1, 0xda81, 0x1a40, 0x1e00, 0xdec1, 0xdf81, 0x1f40, 0xdd01,
        0x1dc0, 0x1c80, 0xdc41, 0x1400, 0xd4c1, 0xd581, 0x1540, 0xd701, 0x17c0,
        0x1680, 0xd641, 0xd201, 0x12c0, 0x1380, 0xd341, 0x1100, 0xd1c1, 0xd081,
        0x1040, 0xf001, 0x30c0, 0x3180, 0xf141, 0x3300, 0xf3c1, 0xf281, 0x3240,
        0x3600, 0xf6c1, 0xf781, 0x3740, 0xf501, 0x35c0, 0x3480, 0xf441, 0x3c00,
        0xfcc1, 0xfd81, 0x3d40, 0xff01, 0x3fc0, 0x3e80, 0xfe41, 0xfa01, 0x3ac0,
        0x3b80, 0xfb41, 0x3900, 0xf9c1, 0xf881, 0x3840, 0x2800, 0xe8c1, 0xe981,
        0x2940, 0xeb01, 0x2bc0, 0x2a80, 0xea41, 0xee01, 0x2ec0, 0x2f80, 0xef41,
        0x2d00, 0xedc1, 0xec81, 0x2c40, 0xe401, 0x24c0, 0x2580, 0xe541, 0x2700,
        0xe7c1, 0xe681, 0x2640, 0x2200, 0xe2c1, 0xe381, 0x2340, 0xe101, 0x21c0,
        0x2080, 0xe041, 0xa001, 0x60c0, 0x6180, 0xa141, 0x6300, 0xa3c1, 0xa281,
        0x6240, 0x6600, 0xa6c1, 0xa781, 0x6740, 0xa501, 0x65c0, 0x6480, 0xa441,
        0x6c00, 0xacc1, 0xad81, 0x6d40, 0xaf01, 0x6fc0, 0x6e80, 0xae41, 0xaa01,
        0x6ac0, 0x6b80, 0xab41, 0x6900, 0xa9c1, 0xa881, 0x6840, 0x7800, 0xb8c1,
        0xb981, 0x7940, 0xbb01, 0x7bc0, 0x7a80, 0xba41, 0xbe01, 0x7ec0, 0x7f80,
        0xbf41, 0x7d00, 0xbdc1, 0xbc81, 0x7c40, 0xb401, 0x74c0, 0x7580, 0xb541,
        0x7700, 0xb7c1, 0xb681, 0x7640, 0x7200, 0xb2c1, 0xb381, 0x7340, 0xb101,
        0x71c0, 0x7080, 0xb041, 0x5000, 0x90c1, 0x9181, 0x5140, 0x9301, 0x53c0,
        0x5280, 0x9241, 0x9601, 0x56c0, 0x5780, 0x9741, 0x5500, 0x95c1, 0x9481,
        0x5440, 0x9c01, 0x5cc0, 0x5d80, 0x9d41, 0x5f00, 0x9fc1, 0x9e81, 0x5e40,
        0x5a00, 0x9ac1, 0x9b81, 0x5b40, 0x9901, 0x59c0, 0x5880, 0x9841, 0x8801,
        0x48c0, 0x4980, 0x8941, 0x4b00, 0x8bc1, 0x8a81, 0x4a40, 0x4e00, 0x8ec1,
        0x8f81, 0x4f40, 0x8d01, 0x4dc0, 0x4c80, 0x8c41, 0x4400, 0x84c1, 0x8581,
        0x4540, 0x8701, 0x47c0, 0x4680, 0x8641, 0x8201, 0x42c0, 0x4380, 0x8341,
        0x4100, 0x81c1, 0x8081, 0x4040
    ]

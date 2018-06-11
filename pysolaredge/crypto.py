import logging
from Crypto.Cipher import AES
import binascii

class Crypto(object):

    cipher = None

    def __init__(self, privkey, payload):
        self.privkey = privkey
        self.payload = payload
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initialized %s' % __name__)
        self.create_cipher()

    def create_cipher(self):
        # encrypt the first part of the 503 message with the private key
        p0 = AES.new(self.privkey).encrypt(self.payload[0:16])
        p1 = self.payload[16:32]
        # XOR each byte of the first part with the corresponding byte in the second part
        tmpkey = bytes((p0[i] ^ p1[i] for i in range(16)))
        self.cipher = AES.new(tmpkey)

    def decrypt(self, payload):
        # This method will return decrypted data or raise an exception
        self.logger.info('Going to decrypt')
        payload = bytearray(payload)
        payload_rand = payload[0:16]
        payload_rand_enc = self.cipher.encrypt(bytes(payload_rand))

        i=0
        j=16

        # 1. For bytes 16 to end of payload, XOR the value with an ENCRYPTED byte from bytes 0-15
        # 2. Cycle the encrypted bytes 0-15, but at the end of every cycle, increase the seed by one and re-encrypt:

        while j < len(payload):
            payload[j] ^= payload_rand_enc[i]
            i += 1
            j += 1
            if i == 16:
                i = 0

                # https://stackoverflow.com/questions/50389707/adding-1-to-a-16-byte-number-in-python
                new_value = int.from_bytes(payload_rand, 'big') + 1
                try:
                    payload_rand = bytearray(new_value.to_bytes(len(payload_rand), 'big'))
                except OverflowError:
                    payload_rand = bytearray(len(payload_rand))

                payload_rand_enc = self.cipher.encrypt(bytes(payload_rand))

        # Not sure what we need this for...
        # 2 bytes, little endian.
        #seqno = int.from_bytes(payload[16:18], 'little')

        data = payload[22:]
        xor  = payload[18:22]

        decrypted = bytearray()
        for i in range(len(data)):
            decrypted.append( data[i] ^ xor[i&3] )

        self.logger.debug('Decrypted data: %s' % binascii.hexlify(decrypted).decode('ascii'))
        return decrypted

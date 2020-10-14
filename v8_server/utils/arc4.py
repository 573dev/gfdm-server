from Crypto.Cipher import ARC4
from Crypto.Hash import MD5


class EamuseARC4(object):
    def __init__(self, eamuse_key):
        # fmt: off
        self.internal_key = bytearray([
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x69, 0xd7,
            0x46, 0x27, 0xd9, 0x85, 0xee, 0x21, 0x87, 0x16,
            0x15, 0x70, 0xd0, 0x8d, 0x93, 0xb1, 0x24, 0x55,
            0x03, 0x5b, 0x6d, 0xf0, 0xd8, 0x20, 0x5d, 0xf5,
        ])
        # fmt: on

        self.key = MD5.new(eamuse_key + self.internal_key[6:]).digest()
        self.arc = ARC4.new(self.key)

    def decrypt(self, data):
        return self.arc.decrypt(bytes(data))

    def encrypt(self, data):
        return self.arc.encrypt(bytes(data))

from Crypto.Cipher import ARC4
from Crypto.Hash import MD5


class EamuseARC4(object):
    def __init__(self, eamuse_key):
        secret_key = 0x69D74627D985EE2187161570D08D93B12455035B6DF0D8205DF5
        key_bytes = bytearray(secret_key.to_bytes(26, "big"))
        key = MD5.new(eamuse_key + key_bytes).digest()
        self.arc = ARC4.new(key)

    def decrypt(self, data):
        return self.arc.decrypt(bytes(data))

    def encrypt(self, data):
        return self.arc.encrypt(bytes(data))

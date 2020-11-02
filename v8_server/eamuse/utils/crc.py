def calculate_crc8(value: str) -> int:
    """
    Calculate the CRC8 of a string representation of an int
    """
    crc = 0

    for c in bytearray(value.encode("ASCII")):
        for i in range(8, 0, -1):
            t = c ^ crc
            crc >>= 1
            if (t & 0x01) != 0:
                crc ^= 0x8C
            c >>= 1
    return crc

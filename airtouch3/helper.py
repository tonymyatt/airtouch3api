def calculate_checksum(message):
    r = 0
    for c in message:
        r += c
    r = (r % 256)
    return bytes([r])

def bit8_in_byte_on(bin_value):
    return (bin_value & 0b10000000) > 0

def bit7_in_byte_on(bin_value):
    return (bin_value & 0b01000000) > 0

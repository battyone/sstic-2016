#!/usr/bin/env python3
import binascii
import os
import struct
import sys

def get_16bytes_from_seed(n):
    """TI pseudo-random number generator"""
    mod1 = 2147483563
    mod2 = 2147483399
    mult1 = 40014
    mult2 = 40692

    if n:
        seed1 = (mult1 * n) % mod1
        seed2 = n % mod2
    else:
        seed1 = 12345
        seed2 = 67890

    result_arr = bytearray(16)
    for i in range(16):
        seed1 = (seed1 * mult1) % mod1
        seed2 = (seed2 * mult2) % mod2;
        result = (seed1 - seed2) / mod1
        if result < 0:
            result = result + 1
        result_arr[i] = int(result * 256.)
    return result_arr


for key in range(0, 2**32):
    if binascii.crc32(struct.pack('<I', key)) == 3298472535:
        print("Key {0} = {0:#x}".format(key))
        code = binascii.hexlify(get_16bytes_from_seed(key)).decode('ascii')
        print("Code: {}".format(code))
        with open('pass.code', 'w') as f:
            f.write(code)
        sys.exit(0)
sys.exit(1)

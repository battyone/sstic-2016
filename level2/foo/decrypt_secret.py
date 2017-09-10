#!/usr/bin/env python3
import binascii

def rotleft(b,n):
    n = n % 8
    return (~((b << n) | (b >> (8 - n)))) & 0xff

data = binascii.unhexlify('cb41dcb1d89746705a7fe998f11acce7')
key = bytes(rotleft(d, i) for i, d in enumerate(data))
code = binascii.hexlify(key).decode('ascii')
with open('pass.code', 'w') as f:
    f.write(code)

#!/usr/bin/env python3
"""Decrypt the data needed for the next level"""
import base64
import binascii
import hashlib
import json
import numpy
import sys
from Crypto.Cipher import AES


# x^128 + x^7 + x^2 + x + 1
GCM_POLY = (1 << 128) + (1 << 7) + (1 << 2) + (1 << 1) + (1 << 0)

def invert_poly(p):
    """Invert the given polynomial in the GCM field"""
    assert p > 0
    assert p.bit_length() <= 128
    e, f = GCM_POLY, p
    l, m = 0, 1
    # m, l so that m * p + l * GCM_POLY = 1
    while f != 1:
        j = f.bit_length() - e.bit_length()
        if j < 0:
            e, f = f, e
            l, m = m, l
            j = -j
        f ^= e << j
        m ^= l << j
    return m


def multiply_poly(x, y):
    """Multiply two polynomials in the GCM field"""
    assert x.bit_length() <= 128
    assert y.bit_length() <= 128
    result = 0
    for bitpos in range(128):
        if y & (1 << bitpos):
            result ^= x
        x = x << 1
        if x.bit_length() > 128:
            x ^= GCM_POLY
    return result

# Sanity checks
assert multiply_poly(2, 1 << 127) == 0x87
assert invert_poly(1) == 1
assert invert_poly(2) == 0x80000000000000000000000000000043
assert multiply_poly(3, invert_poly(3)) == 1


if len(sys.argv) < 4:
    print("Usage: {} path/to/next/data.json path/to/current/data.json path/to/passcode/1 ...".format(sys.argv[0]))
    sys.exit(1)

with open(sys.argv[2]) as data_file:
    jsondata = json.load(data_file)

ssspoints = []

for passcode_path in sys.argv[3:]:
    # Read the code found after solving an enigma
    with open(passcode_path, 'r') as pass_file:
        passcode = binascii.unhexlify(pass_file.read().strip())

    # Decrypt the encrypted shares
    hpass = hashlib.sha256(passcode).hexdigest()
    assert hpass in jsondata['shares'], "Invalid code!"
    iv = binascii.unhexlify(jsondata['shares'][hpass]['iv'])
    data = base64.b64decode(jsondata['shares'][hpass]['data'])
    key = passcode
    decrypted = AES.new(key, AES.MODE_CBC, iv).decrypt(data)
    padlen = decrypted[-1]
    assert all(x == padlen for x in decrypted[-padlen:])
    decrypted = decrypted[:-padlen]

    # Load the new points
    for point in json.loads(decrypted.decode('ascii')):
        # Convert y to a polynom
        ssspoints.append((point['x'], int(point['y'], 16)))

# Interpolate the coefficients of "y = x^2 + a * x + b" curve
assert len(ssspoints) >= 2

x1, y1 = ssspoints[0]
x2, y2 = ssspoints[1]
y1 ^= multiply_poly(x1, x1)
y2 ^= multiply_poly(x2, x2)
coef_a = multiply_poly(y1 ^ y2, invert_poly(x1 ^ x2))
coef_b = y1 ^ multiply_poly(coef_a, x1)
for x, y in ssspoints:
    assert y == multiply_poly(x, x) ^ multiply_poly(coef_a, x) ^ coef_b

# The key is the value of the curve at x=0
key = binascii.unhexlify(hex(coef_b)[2:])

# Decrypt data of next level
iv = binascii.unhexlify(jsondata['next_level']['iv'])
data = base64.b64decode(jsondata['next_level']['data'])
decrypted = AES.new(key, AES.MODE_CBC, iv).decrypt(data)
padlen = decrypted[-1]
assert all(x == padlen for x in decrypted[-padlen:])
decrypted = decrypted[:-padlen]

with open(sys.argv[1], 'wb') as next_file:
    next_file.write(decrypted)

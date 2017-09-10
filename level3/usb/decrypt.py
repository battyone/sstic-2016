#!/usr/bin/env python3
import binascii
import hashlib
import os.path
import struct
import sys

sys.path.insert(0, os.path.dirname(__file__))
import rc4


# Helper functions
def rol32(val, shift):
    val = val & 0xffffffff
    shift = shift & 0x1f
    if not shift:
        return val
    return ((val << shift) & 0xffffffff) | (val >> (32 - shift))

def ror32(val, shift):
    return rol32(val, 32 - shift)


# Load encrypted data
with open('extracted_encrypted_data.bin', 'rb') as f:
    all_data = f.read()

enc_data = all_data[0x40:]

def rc6_decrypt(ks, enc_block):
    """https://en.wikipedia.org/wiki/RC6"""
    a, b, c, d = enc_block
    a -= ks[0xa8 // 4]
    c -= ks[0xac // 4]
    for iround in range(19, -1, -1):
        a, b, c, d = [x & 0xffffffff for x in (d, a, b, c)]
        u = ror32(d * (2 * d + 1), 5)
        t = ror32(b * (2 * b + 1), 5)
        c = rol32(c - ks[2 * iround + 3], t) ^ u
        a = rol32(a - ks[2 * iround + 2], u) ^ t

    d = (d - ks[1]) & 0xffffffff
    b = (b - ks[0]) & 0xffffffff
    return a, b, c, d


# TODO: key derivation with key "551C2016B00B5F00"
key_state = [
    0x2129ab75, 0x975374c8, 0x5eead5ac, 0x2c8b312f,
    0xfd0a1322, 0x80d0133c, 0x16a849c2, 0x42064c4a,
    0x75fe77f5, 0x4ddaf4d7, 0xe9221458, 0x46a97a25,
    0xfea74495, 0xe119d517, 0x055f2605, 0xc6706c81,
    0x4d966822, 0xadc3e831, 0x68c68bdf, 0xfcb57dac,
    0x7df33f01, 0xefb6081f, 0x98eb29eb, 0x668352b7,
    0x98a1545b, 0x0a3e64cd, 0x9b16a929, 0x2233c1c4,
    0x7879ec25, 0x17c4466a, 0x6e0b37ea, 0xde30ebb2,
    0x01ef095c, 0x35fbdb33, 0xa97b35b7, 0xdfbf652c,
    0xaf668798, 0xb7846548, 0xafd8706a, 0x2d346ced,
    0xbb33dfe3, 0xae79adfc, 0xc3115146, 0x05a51471,
]

# Decrypt with RC6-CBC with 128-bit blocks (4 32-bit numbers)
iv = [0, 0, 0, 0]
dec_data = bytearray(len(enc_data))
for blkoffset in range(0, len(enc_data), 16):
    enc_block = struct.unpack('<IIII', enc_data[blkoffset:blkoffset + 16])
    dec_block = rc6_decrypt(key_state, enc_block)
    dec_block = [i ^ d for i, d in zip(iv, dec_block)]
    dec_data[blkoffset:blkoffset + 16] = struct.pack('<IIII', *dec_block)
    iv = enc_block

# dec_data contains chunks
offset = 0
chunk_index = 0
while offset < len(dec_data):
    chunck_length = struct.unpack('<I', dec_data[offset:offset + 4])[0]
    rc4_key = dec_data[offset + 4:offset + 0x14]
    payload_md5 = dec_data[offset + 0x14:offset + 0x24]
    enc_payload = dec_data[offset + 0x24:offset + 0x24 + chunck_length]
    print("Chunk {} at {:#x}: {:#x} bytes".format(chunk_index, offset, chunck_length))

    if chunck_length == 0:
        break

    keystream = rc4.RC4(rc4_key)
    dec_payload = bytearray(e ^ k for e, k in zip(enc_payload, keystream))
    with open('decrypted_chunk_{}.bin'.format(chunk_index), 'wb') as f:
        f.write(dec_payload)

    print("    {}".format(binascii.hexlify(payload_md5).decode('ascii')))
    print("    {}".format(hashlib.md5(dec_payload).hexdigest()))
    assert payload_md5 == hashlib.md5(dec_payload).digest()

    offset += 0x24 + chunck_length
    chunk_index += 1
"""
Chunk 0 at 0x0: 0x39 bytes
    a83bd78eaf49903dfd64447fcd35831a
    a83bd78eaf49903dfd64447fcd35831a
Chunk 1 at 0x5d: 0xc15 bytes
    ad2713a0668ac3f421a00b7b21430b4f
    ad2713a0668ac3f421a00b7b21430b4f
Chunk 2 at 0xc96: 0x34631 bytes
    671d51af77f541605ea91e81e8dc70f0
    671d51af77f541605ea91e81e8dc70f0
Chunk 3 at 0x352eb: 0x1b234 bytes
    8ff9f891acf83a5ee95f69084b4d48d2
    8ff9f891acf83a5ee95f69084b4d48d2
Chunk 4 at 0x50543: 0xfbe0 bytes
    c4e5abbc8c4ddff3853db0fcb9eb55ff
    c4e5abbc8c4ddff3853db0fcb9eb55ff
Chunk 5 at 0x60147: 0xb9f7 bytes
    0cb3389fedc86b4ff4a86db0b492b273
    0cb3389fedc86b4ff4a86db0b492b273
Chunk 6 at 0x6bb62: 0x83d5 bytes
    03d5e4c549945d4ac5b1e3b973606d61
    03d5e4c549945d4ac5b1e3b973606d61
Chunk 7 at 0x73f5b: 0x12500a bytes
    581ae98e6119f7672ba38c74b1c427ce
    581ae98e6119f7672ba38c74b1c427ce
Chunk 8 at 0x198f89: 0x0 bytes
"""

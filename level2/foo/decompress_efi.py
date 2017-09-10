#!/usr/bin/env python
import EfiCompressor
import binascii


d = binascii.unhexlify(
    '3f0000005c000000003c4c8d823302ed6400b717307da812af1b021dfab86124fe3b24f5'
    '1fccce8ba7738572726a518f09c1d4b10c7ba3a1b3cf078fcd9d553475ded963832000')
print(''.join(EfiCompressor.UefiDecompress(d, len(d))).decode('utf16'))
# => secret data: cb41dcb1d89746705a7fe998f11acce7

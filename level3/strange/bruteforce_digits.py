#!/usr/bin/env python3
"""Bruteforce the digits of the key using the neural network"""
import numpy

def sigmoid(val):
    val = 1. / (1. + numpy.exp(-val))
    return val


ALL_DATA = numpy.fromfile('196', dtype=numpy.double)
assert len(ALL_DATA) == 65860*32

found = ['*'] * 32
for block_index in range(32):
    for tested_digit in range(10):
        # Test the image for digit "tested_digit"
        data_pos = (tested_digit + 9) * 65860
        image = [1 if x > .5 else 0 for x in ALL_DATA[data_pos:data_pos+400]]

        # Run the 160 first neurons
        intermediate = numpy.empty(160)
        for ineur in range(160):
            data_pos = block_index * 65860 + 400 + 405 * ineur
            val = ALL_DATA[data_pos + 2]  # bias
            val += numpy.dot(ALL_DATA[data_pos + 3:data_pos + 403], image)  # weight
            intermediate[ineur] = sigmoid(val)

        # Run the 4 last neurons
        final_vect = numpy.empty(4)
        for ineur in range(4):
            data_pos = block_index * 65860 + 65200 + 165 * ineur
            val = ALL_DATA[data_pos + 2]
            val += numpy.dot(ALL_DATA[data_pos + 3:data_pos + 163], intermediate)
            final_vect[ineur] = sigmoid(val)

        if all(r < 0.15 for r in final_vect):
            print("{}: found {}".format(block_index, tested_digit))
            found[block_index] = str(tested_digit)

code = ''.join(found)
print(code)
with open('pass.code', 'w') as f:
    f.write(code)

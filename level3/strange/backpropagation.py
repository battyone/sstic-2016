#!/usr/bin/env python3
"""Solve strange with backpropagation"""
import chainer
import numpy

from chainer import cuda, Function, gradient_check, Variable, optimizers, serializers, utils
from chainer import Link, Chain, ChainList
import chainer.functions as F
import chainer.links as L

class strangeNN(Chain):
    def __init__(self, data):
        first_neurons = F.Linear(400, 160)
        for ineur in range(160):
            data_pos = 400 + 405 * ineur
            first_neurons.W.data[ineur][:] = data[data_pos + 3:data_pos + 403]
            first_neurons.b.data[ineur] = data[data_pos + 2]

        last_neurons = F.Linear(160, 4)
        for ineur in range(4):
            data_pos = 65200 + 165 * ineur
            last_neurons.W.data[ineur][:] = data[data_pos + 3:data_pos + 163]
            last_neurons.b.data[ineur] = data[data_pos + 2]

        super(strangeNN, self).__init__(
            first_neurons=first_neurons,
            last_neurons=last_neurons,
        )

    def __call__(self, x):
        y = F.sigmoid(self.first_neurons(x))
        return F.sigmoid(self.last_neurons(y))


ALL_DATA = numpy.fromfile('196', dtype=numpy.double)
assert len(ALL_DATA) == 65860 * 32

IM400_ZEROS = numpy.zeros((1, 400), dtype=numpy.float32)
IM400_ONES = numpy.ones((1, 400), dtype=numpy.float32)

for block_index in range(32):
    model = strangeNN(ALL_DATA[65860 * block_index:65860 * (block_index + 1)])
    image_data = numpy.ones((1, 400), dtype=numpy.float32) / 2

    for grad_iteration in range(5000):
        # Forward...
        image = chainer.Variable(image_data)
        result = model(image)
        # ... and backward
        result.grad = -result.data
        result.backward()
        image_data += image.grad
        # Clamp the image pixels between 0 and 1
        image_data = numpy.maximum(image_data, IM400_ZEROS)
        image_data = numpy.minimum(image_data, IM400_ONES)

        if 0 and not (grad_iteration % 500):
            # Make the image white and black again
            for i, x in enumerate(image_data[0]):
                image_data[0][i] = 1 if x > .8 else 0 if x < .2 else .5

    print(result.data, '23425038472508287335772085544035'[block_index])
    for y in range(20):
        line = ['  ..::;;XX#'[int(image_data[0][20 * y + x] * 10)] for x in range(20)]
        print(''.join(line))

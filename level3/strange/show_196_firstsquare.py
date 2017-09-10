#!/usr/bin/python3
"""Show the image taken from the 32 first 20x20 squares of file 196"""
from PIL import Image, ImageDraw
import struct

im = Image.new("RGB", (20 * 32, 20), "white")
draw = ImageDraw.Draw(im)
with open('196', 'rb') as f:
    for iframe in range(32):
        fdata = f.read(65860 * 8)
        assert len(fdata) == 65860 * 8

        for y in range(20):
            for x in range(20):
                pos = (y * 20 + x) * 8
                val = struct.unpack('<d', fdata[pos:pos + 8])[0]
                graycol = 255 if val < 0.5 else 0
                draw.rectangle(
                    (iframe * 20 + x, y, iframe * 20 + x + 1, y + 1),
                    (graycol, graycol, graycol))

    assert f.read() == b''

im.show()

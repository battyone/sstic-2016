#!/usr/bin/env python3
"""Extract img.bz2 partitions and data

fdisk -l img:

    Device Boot   Start     End Sectors  Size Id Type
    img1              3 2097154 2097152    1G  b W95 FAT32
    img2        2099201 3147775 1048575  512M  b W95 FAT32
    img3        3147777 3168256   20480   10M  b W95 FAT32
    img4        3168257 3987455  819199  400M  b W95 FAT32

Mapping:

    00000000..00000200: MBR
    00000200..00000600: (encrypted data)
    00000600..40000600: part1
    40000600..40100200: (encrypted data)
    40100200..60100000: part2
    60100000..60100200: (encrypted data)
    60100200..60b00200: part3
    60b00200..79b00000: part4
    79b00000..79b98e00: (encrypted data)
"""
import bz2

disk_sect_offsets = (
    (3, 2097154),
    (2099201, 3147775),
    (3147777, 3168256),
    (3168257, 3987455),
)

# Split into components, use None for encrypted data
components_offsets = [(0, 512, 'MBR')]
last_offset = 512
for partnum, offsets in enumerate(disk_sect_offsets):
    start, stop = offsets
    offset = 512 * start
    if offset > last_offset:
        components_offsets.append((last_offset, offset - last_offset, None))
    last_offset = 512 * (stop + 1)
    components_offsets.append((offset, last_offset - offset, 'part{}'.format(partnum + 1)))

encrypted_data = b''
with bz2.BZ2File('img.bz2', 'rb') as fimg:
    current_offset = 0
    for offset, size, name in components_offsets:
        assert current_offset == offset
        print("{:08x}..{:08x}: {}".format(offset, offset + size, name or "(encrypted data)"))
        data = fimg.read(size)
        assert len(data) == size
        current_offset = offset + size

        if name:
            with open('extracted_{}.bin'.format(name), 'wb') as f:
                f.write(data)
        else:
            encrypted_data += data

    final_data = fimg.read(0xa0000)
    assert final_data.endswith(b'\0' * 512)
    final_data = final_data.rstrip(b'\0')
    encrypted_data += final_data
    print("{:08x}..{:08x}: (encrypted data)".format(current_offset, current_offset + len(final_data)))

with open('extracted_encrypted_data.bin', 'wb') as f:
    f.write(encrypted_data)

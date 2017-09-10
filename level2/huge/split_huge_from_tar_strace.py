#!/usr/bin/env python3
import codecs
import re

def trans_addr(addr):
    """Traduit une position de fichier en une adresse du programme"""
    if addr < 0x1000:
        return 0
    if 0x0000000000001000 <= addr < 0x0000000000001000 + 0x00001ef000000000:
        return 0x00002b0000000000 + addr - 0x0000000000001000
    if 0x00002afffffe1000 <= addr < 0x00002afffffe1000 + 0x0000161000000000:
        return 0x000049f000000000 + addr - 0x00002afffffe1000
    if 0x000049effffe1000 <= addr < 0x000049effffe1000 + 0x00002afffffe0000:
        return 0x0000000000020000 + addr - 0x000049effffe1000
    raise Exception("Invalid addr {:#x}".format(addr))

blobs = {}
with open('strace_tar_output.log', 'r') as f:
    curseek = 0
    for line in f:
        m = re.match(r'lseek\(4, ([^,]*), SEEK_SET\)', line)
        if m is not None:
            curseek = int(m.group(1))
            continue
        if line.startswith('write(4, "'):
            m = re.match(r'write\(4, "(.*)", ([0-9]*)\) = ([0-9]*)', line)
            assert m is not None:
            rawdata, count1, count2 = m.groups()
            assert count1 == count2

            addr = curseek
            curseek += int(count1)
            data = codecs.escape_decode(rawdata.encode('ascii'))[0]
            # Trouve le premier octet non-nul dans le bloc de données
            i = 0
            while i < len(data) and not data[i]:
                i += 1
            if i >= len(data):
                continue

            addr = trans_addr(addr + i)
            data = data[i:].rstrip(b'\0')
            with open('out/blob-{:016x}.bin'.format(addr), 'wb') as f:
                f.write(data)

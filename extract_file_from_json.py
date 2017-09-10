#!/usr/bin/env python
"""Extract a file embedded in a JSON file"""
import base64
import json
import os.path
import sys

if len(sys.argv) != 3:
    print("Usage: {} path/to/data.json path/to/extracted/file".format(sys.argv[0]))
    sys.exit(1)

with open(sys.argv[1]) as data_file:
    data = json.load(data_file)

filepath = sys.argv[2]
filename = os.path.basename(filepath)
if filename not in data['files']:
    print("Unknown file")
    sys.exit(1)

with open(filepath, 'wb') as file_out:
    file_out.write(base64.b64decode(data['files'][filename]))

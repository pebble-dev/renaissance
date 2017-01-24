#!/usr/bin/env python3

import argparse
import json
import os.path
import struct
import sys
from enum import Enum

# Copyright (c) 2017 Johannes Neubrand
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


class Features(Enum):
    # A simple enum which defines bitmasks & their corresponding values
    OFFSET_SIZE_MASK = 0b01
    OFFSET_SIZE_VALUES = {0: 4, 0b1: 2}
    ENCODING_MASK = 0b10
    ENCODING_VALUES = {0: 'bmp', 0b10: 'rle4'}


class FileReader():
    # A wrapper around the file class.
    # This is used to make byte counting less tedious.
    def __init__(self, fh):
        self.fh = fh
        self.bytes_read = 0

    def read(self, byte_amt):
        self.bytes_read += byte_amt
        return self.fh.read(byte_amt)

    def read_all(self):
        data = self.fh.read()
        self.bytes_read += len(data)
        return data


class FontReader:
    # The actual font reader.
    def read(self, fh):
        fh = FileReader(fh)

        # Read FontInfo

        (version,            # B
         max_height,         # B
         glyph_amt,          # H
         fallback_codepoint  # H
         ) = struct.unpack('<BBHH', fh.read(6))

        # Set defaults in case we're operating on earlier versions
        hash_table_size = 255
        codepoint_bytes = None
        size = None
        features = 0

        if version >= 2:
            (hash_table_size,  # B
             codepoint_bytes   # B
             ) = struct.unpack('<BB', fh.read(2))

        if version >= 3:
            (size,     # B
             features  # B
             ) = struct.unpack('<BB', fh.read(2))

        offset_bytes = Features.OFFSET_SIZE_VALUES.value[
            features & (Features.OFFSET_SIZE_MASK.value)]

        # ----------------------------------------------------------------------

        # Read HashTable

        offset_table_data = []

        for _hash_iter in range(hash_table_size):
            (hash_value,           # B
             offset_table_size,    # B
             offset_table_offset,  # H
             ) = struct.unpack('<BBH', fh.read(4))
            offset_table_data += [{'hash': hash_value,
                                   'size': offset_table_size,
                                   'offset': offset_table_offset}]

        offset_table_data.sort(key=lambda x: x['offset'])

        # ----------------------------------------------------------------------

        # Read OffsetTable

        first_offset_item_offset = fh.bytes_read

        glyph_table_data = []

        for offset_list in offset_table_data:
            if (offset_list['offset'] !=
                    fh.bytes_read - first_offset_item_offset):
                raise Exception('Offset item at incorrect offset')
            for codepoint_index in range(offset_list['size']):
                (codepoint,  # B or H, depending on codepoint_bytes
                 offset      # B or H, depending on features
                 ) = struct.unpack(
                    '<' +
                    ('H' if codepoint_bytes == 2 else 'I') +
                    ('H' if offset_bytes == 2 else 'I'),
                    fh.read(codepoint_bytes + offset_bytes))
                glyph_table_data += [{'codepoint': codepoint,
                                      'offset': offset}]

        # ----------------------------------------------------------------------

        # Read GlyphData

        glyph_data = fh.read_all()

        glyph_list = []

        for glyph in glyph_table_data:
            if (glyph['offset'] + 7) > len(glyph_data):
                raise Exception('Glyph offset too large.', glyph)
            (width,
             height,
             left,
             top,
             advance) = struct.unpack(
                '<BBBBBxxx', glyph_data[glyph['offset']:glyph['offset'] + 8])
            glyph_list += [{'character': chr(glyph['codepoint']),
                            'codepoint': glyph['codepoint'],
                            'width': width,
                            'height': height,
                            'left': left,
                            'top': top,
                            'advance': advance}]

        # ----------------------------------------------------------------------

        glyph_list.sort(key=lambda a: a['codepoint'])

        print('Processed %d bytes.' % fh.bytes_read, file=sys.stderr)
        return {'line-height': max_height,
                'fallback': fallback_codepoint,
                'glyphs': glyph_list}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+',
                        help='files to be parsed')
    a = parser.parse_args()
    data = {}
    for f in a.files:
        with open(f, 'rb') as fh:
            r = FontReader()
            if (os.path.split(f)[-1]) in data:
                print('file named', os.path.split(f)[-1],
                      'already processed; skipping')
            data[os.path.split(f)[-1]] = r.read(fh)
    json.dump(data, sys.stdout, indent=2)

###############################################################################
#                                                                             #
#           An interface to read pbff files, manipulate their data,           #
#              write pbff files, and write binary font files.                 #
#                                                                             #
###############################################################################

from .io import *
import itertools
import re
import struct
import sys
import unicodedata

# Copyright (c) 2017 jneubrand
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


class Font():
    def __init__(self, fh):
        f1 = LinedFileReader(fh)
        self.glyphs = {}
        while not f1.empty():
            line = f1.next()

            # This regex structure isn't a nice solution. Please open a PR or
            #     tell me if you know of a better one ;)

            r = re.match(r'^\s*$/', line)
            if r:
                continue

            r = re.match(r'^line-height (\d+)$', line)
            if r:
                self.line_height = int(r.group(1))
                continue

            r = re.match(r'^version (\d+)$', line)
            if r:
                self.version = int(r.group(1))
                continue

            r = re.match(r'^fallback (\d+)$', line)
            if r:
                self.fallback_codepoint = int(r.group(1))
                continue

            r = re.match(r'^glyph (\d+)', line)
            if r:
                glyph_codepoint = int(r.group(1))
                data = []
                r = re.match(r'^(\s*)(-+|\.)\s*(\d+)$', f1.next())
                if r:
                    negativeLeft = len(r.group(1))
                    advance = 0 if r.group(2) == '.' else len(r.group(2))
                    top = int(r.group(3))
                    r = re.match(r'^([ #]*)$', f1.peek())
                    while r:
                        f1.next()
                        data += [[True if x == '#' else False
                                  for x in r.group(1)]]
                        r = re.match(r'^([ #]*)$', f1.peek())
                    first_enabled = None
                    last_enabled = 0
                    for bmpline in data:
                        idx = 0
                        for char in bmpline:
                            if char and (first_enabled is None or
                                         idx < first_enabled):
                                first_enabled = idx
                            if char and idx > last_enabled:
                                last_enabled = idx
                            idx += 1
                    for bmpline in data:
                        while len(bmpline) <= last_enabled:
                            bmpline += [False]
                    data = [x[first_enabled:] for x in data]
                    if first_enabled is None:
                        left = 0
                        width = 0
                        height = 0
                    else:
                        left = first_enabled - negativeLeft
                        width = last_enabled - first_enabled + 1
                        height = len(data)
                    self.glyphs[glyph_codepoint] = {
                        'top': top,
                        'data': data,
                        'left': left,
                        'width': width,
                        'height': height,
                        'advance': advance
                    }
                else:
                    raise Error('Invalid data')

    def output(self, out=sys.stdout):
        print('version %d' % self.version, file=out)
        print('fallback %d' % self.fallback_codepoint, file=out)
        print('line-height %d' % self.line_height, file=out)
        for codepoint in sorted(self.glyphs.keys()):
            glyph = self.glyphs[codepoint]
            print('glyph %d%s' % (
                codepoint,
                ' ' + chr(codepoint)
                if unicodedata.category(chr(codepoint)) not in ['Cc']
                else ''),
                file=out)
            if glyph['left'] < 0:
                print(' ' * -glyph['left'], end='', file=out)
            print('-' * glyph['advance'], end='', file=out)
            if glyph['advance'] == 0:
                print('.')
            print(' %d' % glyph['top'], file=out)

            for row in glyph['data']:
                if glyph['left'] > 0:
                    print(' ' * glyph['left'], end='', file=out)
                for pixel in row:
                    print('#' if pixel else ' ', end='', file=out)
                print('', file=out)

            print('-', file=out)

    def output_font(self, fh):

        def group_codepoints(codepoints, glyph_amt):
            hasher = lambda x: x % glyph_amt
            return itertools.groupby(
                sorted(codepoints, key=hasher), key=hasher)

        def get_bytes(bits):
            while len(bits):
                item = 0
                for x in range(8):
                    item <<= 1
                    item += bits.pop(7 - x)
                yield item

        def generate_glyph_table(glyphs, fallback_codepoint):
            out = struct.pack('<xxxx')
            metadata = {}
            written = 4
            glyph_order = [fallback_codepoint] + \
                sorted(x for x in glyphs.keys() if x != 9647)
            for codepoint in glyph_order:
                metadata[codepoint] = written

                glyph = glyphs[codepoint]

                out += struct.pack('<BBbbb',
                                   glyph['width'],
                                   glyph['height'],
                                   glyph['left'],
                                   glyph['top'],
                                   glyph['advance'])
                written += 5

                # out += struct.pack('<BBB', 0, 0, 0)
                # written += 3

                bits = sum(glyph['data'], [])
                assert len(bits) == glyph['width'] * glyph['height']
                while (len(bits) % 32):
                    bits = bits + [False]
                for byte in get_bytes(bits):
                    written += 1
                    out += struct.pack('<B', byte)
            return out, metadata

        def generate_offset_table(glyphs, glyph_metadata,
                                  hash_table_len,
                                  codepoint_bytes, offset_bytes):
            out = b''
            metadata = {}
            written = 0

            for hash_value, group in group_codepoints(glyphs.keys(),
                                                      hash_table_len):
                group = list(group)
                metadata[hash_value] = {'pos': written, 'size': len(group)}
                for codepoint in group:
                    out += struct.pack(
                        ('<H' if codepoint_bytes == 2 else '<L') +
                        ('H' if offset_bytes == 2 else 'L'),
                        codepoint,
                        glyph_metadata[codepoint])
                    written += codepoint_bytes + offset_bytes
            return out, metadata

        def generate_hash_table(offset_metadata):
            out = b''
            for hashval in range(255):
                if hashval not in offset_metadata:
                    out += struct.pack('<BBH', hashval, 0, 0)
                else:
                    out += struct.pack('<BBH',
                                       hashval,
                                       offset_metadata[hashval]['size'],
                                       offset_metadata[hashval]['pos'])
            return out

        hash_table_len = 255

        fh.write(struct.pack('<BBHH',
                             self.version,
                             self.line_height,
                             len(self.glyphs),
                             self.fallback_codepoint))

        codepoint_bytes = 4
        if self.version >= 2:
            if max(self.glyphs.keys()) < 0xFFFF:
                codepoint_bytes = 2
                print('using 2 as codepoint bytes', file=sys.stderr)
            fh.write(struct.pack('<BB',
                                 hash_table_len,
                                 codepoint_bytes))
        if self.version >= 3:
            fh.write(struct.pack('<BB',
                                 10,  # Fontinfo Size
                                 0))   # TODO features

        glyph_out, glyph_metadata = \
            generate_glyph_table(self.glyphs, self.fallback_codepoint)
        offset_out, offset_metadata = \
            generate_offset_table(self.glyphs, glyph_metadata,
                                  hash_table_len, codepoint_bytes, 4)
        # Currently using 4 byte offset widths for everything.
        # TODO change this when v3 support is implemented

        hash_out = \
            generate_hash_table(offset_metadata)

        fh.write(hash_out)
        fh.write(offset_out)
        fh.write(glyph_out)

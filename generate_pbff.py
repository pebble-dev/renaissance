#!/usr/bin/env python3

###############################################################################
#                                                                             #
#                     Reads a metrics.json dump and outputs                   #
#                pbff files based on the data contained therein.              #
#                                                                             #
###############################################################################

import argparse
import json
import os
import string
import sys
import unicodedata

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


def generate_pbff_file(data, out):
    print('version %d' % 3, file=out)
    print('fallback %d' % data['fallback'], file=out)
    print('line-height %d' % data['line-height'], file=out)
    for glyph in data['glyphs']:
        (top, left, advance, width, height, codepoint) = \
            (glyph[x] for x in
             ('top', 'left', 'advance', 'width', 'height', 'codepoint'))

        print('glyph %d%s' % (
            codepoint,
            ' ' + chr(codepoint)
            if unicodedata.category(chr(codepoint)) not in ['Cc'] else 'asdf'),
            file=out)
        if left < 0:
            print(' ' * -left, end='', file=out)
        print('-' * advance, end='', file=out)
        if advance == 0:
            print('.')
        print(' %d' % top, file=out)

        for x in range(height):
            if left > 0:
                print(' ' * left, end='', file=out)
            print('#' * width, file=out)

        print('-', file=out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file',
                        help='json file to be parsed')
    a = parser.parse_args()
    data = {}
    if not os.path.isdir('out'):
        os.mkdir('out')
    with open(a.file, 'r') as fh:
        data = json.load(fh)
        for name, fontdata in data.items():
            with open(os.path.join('out', name + '.pbff'), 'w') as out:
                generate_pbff_file(fontdata, out)

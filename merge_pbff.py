#!/usr/bin/env python3

###############################################################################
#                                                                             #
#                   Copies glyph data from file A to file B                   #
#                    while preserving metrics from file B.                    #
#                                                                             #
###############################################################################

import argparse
import json
import os.path
import re
import struct
import sys
from lib.pbff import *

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


def process(fh1, fh2, out=sys.stdout):
    font1 = Font(fh1)
    font2 = Font(fh2)
    processed_codepoints = []
    for codepoint in font2.glyphs.keys():
        processed_codepoints += [codepoint]
        if codepoint not in font1.glyphs:
            continue
        glyph_o = font1.glyphs[codepoint]
        glyph = font2.glyphs[codepoint]
        glyph['data'] = [y[:] for y in font1.glyphs[codepoint]['data']]

        while len(glyph['data']) < glyph['height']:
            glyph['data'] += [[True * glyph['width']]]
        while len(glyph['data']) > glyph['height']:
            del glyph['data'][-1]

        for line in glyph['data']:
            while len(line) < glyph_o['width']:
                line += [False]
            while len(line) < glyph['width']:
                line += [True]
            if len(line) > glyph['width']:
                line = line[:glyph['width']]
        font2.glyphs[codepoint] = glyph
    font2.output()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file1',
                        help='file whose glyphs to take')
    parser.add_argument('file2',
                        help='file whose glyphs to replace')
    a = parser.parse_args()
    with open(a.file1, 'r') as f1, open(a.file2, 'r') as f2:
        process(f1, f2)

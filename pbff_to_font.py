#!/usr/bin/env python3

###############################################################################
#                                                                             #
#                 Converts pbff files to pebble font files.                   #
#                                                                             #
###############################################################################

from lib.pbff import Font
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='+',
                        help='pbff file to be parsed')
    a = parser.parse_args()
    data = {}
    if not os.path.isdir('fonts'):
        os.mkdir('fonts')
    for f in a.file:
        with open(f, 'r') as fh,\
                open(os.path.join('fonts',
                     os.path.basename(f).replace('.pbff', '.pbf')), 'wb')\
                as out:
            print(Font(fh).output_font(out))

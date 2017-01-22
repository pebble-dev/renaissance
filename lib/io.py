###############################################################################
#                                                                             #
#                 File wrappers that keep track of bytes read.                #
#              These help keep you from going absolutely insane.              #
#                                                                             #
###############################################################################

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


class LinedFileReader():
    def __init__(self, fh):
        self.data = fh.readlines()
        self.bytes_read = 0

    def empty(self):
        return len(self.data) == 0

    def next(self):
        t = self.data[0]
        del self.data[0]
        return t.replace('\n', '')

    def peek(self):
        return self.data[0].replace('\n', '')


class FileReader():
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

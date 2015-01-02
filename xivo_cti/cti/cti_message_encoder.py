# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import cjson
import time


class CTIMessageDecoder(object):
    # Contrary to the CTIMessageEncoder, this is stateful, so an instance
    # of this class can't be shared.

    def __init__(self):
        self._buf = ''

    def decode(self, data):
        buf = self._buf + data
        lines = buf.split('\n')
        self._buf = lines[-1]
        return [self._decode_line(line) for line in lines[:-1]]

    def _decode_line(self, line):
        # Output of the cjson.decode is a Unicode object, even though the
        # non-ASCII characters have not been decoded.
        # Without the .decode('utf-8'), some Unicode character (try asian, not european)
        # will not be interpreted correctly.
        return cjson.decode(line.decode('utf-8').replace('\\/', '/'))


class CTIMessageEncoder(object):

    def encode(self, msg):
        msg['timenow'] = time.time()
        return cjson.encode(msg) + '\n'

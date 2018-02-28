# -*- coding: utf-8 -*-
# Copyright (C) 2014-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import json
import time


class CTIMessageCodec(object):

    def __init__(self):
        self._encoder = CTIMessageEncoder()

    def new_decoder(self):
        return CTIMessageDecoder()

    def new_encoder(self):
        return self._encoder


class CTIMessageDecoder(object):

    def __init__(self):
        self._buf = ''

    def decode(self, data):
        buf = self._buf + data
        lines = buf.split('\n')
        self._buf = lines[-1]
        return [self._decode_line(line) for line in lines[:-1]]

    def _decode_line(self, line):
        return json.loads(line)


class CTIMessageEncoder(object):

    def encode(self, msg):
        msg['timenow'] = time.time()
        return json.dumps(msg) + '\n'

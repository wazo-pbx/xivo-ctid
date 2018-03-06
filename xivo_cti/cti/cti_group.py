# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from collections import deque
from xivo_cti.client_connection import ClientConnection

logger = logging.getLogger(__name__)


class CTIGroup(object):

    def __init__(self, cti_msg_encoder, flusher):
        self._cti_msg_encoder = cti_msg_encoder
        self._flusher = flusher
        self._interfaces = set()
        self._buffer = deque()

    def add(self, interface_cti):
        self._interfaces.add(interface_cti)

    def remove(self, interface_cti):
        self._interfaces.discard(interface_cti)

    def send_message(self, msg):
        if not self._buffer:
            self._flusher.add(self)

        self._buffer.append(self._cti_msg_encoder.encode(msg))

    def flush(self):
        data = self._reset_buffer()
        closed_interfaces = []
        for interface_cti in self._interfaces:
            try:
                interface_cti.send_encoded_message(data)
            except ClientConnection.CloseException:
                logger.info('could not send message to %s: connection closed', interface_cti)
                closed_interfaces.append(interface_cti)

        for closed_interface in closed_interfaces:
            self._interfaces.remove(closed_interface)

    def _reset_buffer(self):
        data = ''.join(self._buffer)
        self._buffer.clear()
        return data


class CTIGroupFactory(object):

    def __init__(self, cti_msg_codec, flusher):
        self._cti_msg_codec = cti_msg_codec
        self._flusher = flusher

    def new_cti_group(self):
        return CTIGroup(self._cti_msg_codec.new_encoder(), self._flusher)

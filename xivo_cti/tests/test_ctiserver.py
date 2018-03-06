# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock
from xivo_cti.ctiserver import CTIServer
from xivo_cti.cti.cti_group import CTIGroup


class TestCTIServer(unittest.TestCase):

    def setUp(self):
        self.broadcast_cti_group = Mock(CTIGroup)
        self.cti_server = CTIServer()
        self.cti_server._broadcast_cti_group = self.broadcast_cti_group

    def test_send_cti_event(self):
        event = {'event': 'My test event'}

        self.cti_server.send_cti_event(event)

        self.broadcast_cti_group.send_message.assert_called_once_with(event)

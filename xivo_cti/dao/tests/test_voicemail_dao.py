# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock
from hamcrest import assert_that
from hamcrest import equal_to
from xivo_cti import innerdata
from xivo_cti import dao


class TestVoicemailDAO(unittest.TestCase):

    def setUp(self):
        self.innerdata = Mock(innerdata.Safe)

    def test_get_number(self):
        vm_id = '3'
        vm_number = '3456'

        vm_config = Mock()
        vm_config.keeplist = {vm_id: {'mailbox': vm_number}}
        self.innerdata.xod_config = {'voicemails': vm_config}
        dao.voicemail = dao.VoicemailDAO(self.innerdata)

        assert_that(dao.voicemail.get_number(vm_id), equal_to(vm_number), 'Voicemail number')

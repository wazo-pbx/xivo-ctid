# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

import unittest
from mock import Mock, NonCallableMock
from xivo_cti.interfaces.interface_webi import WEBI
from xivo_cti.ctiserver import CTIServer
from xivo_cti.ioc.context import context
from xivo_cti.cti_config import Config
from xivo_cti.services.queue_member.updater import QueueMemberUpdater


class Test(unittest.TestCase):
    def setUp(self):
        mock_config = NonCallableMock(Config)
        mock_config.getconfig.return_value = {'live_reload_conf': True}
        context.register('cti_config', mock_config)
        self._ctiserver = Mock(CTIServer)
        self._queue_member_updater = Mock(QueueMemberUpdater)
        self._interface_webi = WEBI(self._ctiserver, self._queue_member_updater)

    def tearDown(self):
        context.reset()

    def test_manage_connection_reload_daemon(self):
        raw_msg = 'xivo[daemon,reload]'
        expected_result = [{'message': [],
                            'closemenow': True}]

        result = self._interface_webi.manage_connection(raw_msg)

        self.assertEqual(self._ctiserver.askedtoquit, True)
        self.assertEqual(expected_result, result)

    def test_manage_connection_unknown_msg(self):
        raw_msg = 'command that does_not exist'
        expected_result = [{'message': [],
                            'closemenow': True}]
        self._interface_webi._send_ami_request = Mock()

        result = self._interface_webi.manage_connection(raw_msg)

        self._interface_webi._send_ami_request.assert_never_called()
        self.assertEqual(expected_result, result)

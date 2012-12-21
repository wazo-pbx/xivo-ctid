# -*- coding: UTF-8 -*-

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
        context.register('config', mock_config)
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

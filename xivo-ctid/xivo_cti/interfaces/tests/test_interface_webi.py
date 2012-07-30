# -*- coding: UTF-8 -*-

import unittest
from xivo_cti.interfaces.interface_webi import WEBI, _CMD_WEBI_PATTERN
from xivo_cti.ctiserver import CTIServer
from tests.mock import Mock
from xivo_cti import cti_config
from xivo_cti.services.queuemember_service_manager import QueueMemberServiceManager


class Test(unittest.TestCase):
    def setUp(self):
        self._ctiserver = Mock(CTIServer)
        self._interface_webi = WEBI(self._ctiserver)
        self._interface_webi._config = Mock(cti_config)
        self._interface_webi._config.getconfig = Mock()
        self._interface_webi._config.getconfig.return_value = {'live_reload_conf': True}

    def test_manage_connection_reload_daemon(self):
        raw_msg = 'xivo[daemon,reload]'
        expected_result = [{'message': [],
                            'closemenow': True}]

        result = self._interface_webi.manage_connection(raw_msg)

        self.assertEqual(self._ctiserver.askedtoquit, True)
        self.assertEqual(expected_result, result)

    def test_manage_connection_queuemember_update(self):
        raw_msg = 'xivo[queuemember,update]'
        expected_result = [{'message': [],
                            'closemenow': True}]
        self._interface_webi.queuemember_service_manager = Mock(QueueMemberServiceManager)

        result = self._interface_webi.manage_connection(raw_msg)

        self._interface_webi.queuemember_service_manager.update_config.assert_called_once_with()
        self.assertEqual(expected_result, result)

    def test_manage_connection_unknown_msg(self):
        raw_msg = 'command that does_not exist'
        expected_result = [{'message': [],
                            'closemenow': True}]
        self._interface_webi._send_ami_request = Mock()

        result = self._interface_webi.manage_connection(raw_msg)

        self._interface_webi._send_ami_request.assert_never_called()
        self.assertEqual(expected_result, result)

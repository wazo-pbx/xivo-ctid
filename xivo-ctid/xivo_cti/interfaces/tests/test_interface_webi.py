# -*- coding: UTF-8 -*-

import unittest
from xivo_cti.interfaces.interface_webi import WEBI, BadWebiCommandException
from xivo_cti.ctiserver import CTIServer
from tests.mock import Mock
from xivo_cti import cti_config
from xivo_cti.interfaces.interface_ami import AMI
from xivo_cti.services.queuemember_service_manager import QueueMemberServiceManager


class Test(unittest.TestCase):
    def setUp(self):
        self._ctiserver = Mock(CTIServer)
        self._interface_webi = WEBI(self._ctiserver)
        self._interface_webi._config = Mock(cti_config)
        self._interface_webi._config.getconfig = Mock()
        self._interface_webi._config.getconfig.return_value = {'live_reload_conf': True}

    def tearDown(self):
        pass

    def test_parse_webi_command_async(self):
        raw_msg = 'async:dialplan reload'
        expected_type = 'async'
        expected_msg = 'dialplan reload'

        type, msg = self._interface_webi._parse_webi_command(raw_msg)

        self.assertEqual(expected_type, type)
        self.assertEqual(expected_msg, msg)

    def test_parse_webi_command_sync(self):
        raw_msg = 'sync:dialplan reload'
        expected_type = 'sync'
        expected_msg = 'dialplan reload'

        type, msg = self._interface_webi._parse_webi_command(raw_msg)

        self.assertEqual(expected_type, type)
        self.assertEqual(expected_msg, msg)

    def test_parse_webi_command_empty(self):
        raw_msg = ''

        self.assertRaises(BadWebiCommandException, self._interface_webi._parse_webi_command, raw_msg)

    def test_parse_webi_command_empty_msg(self):
        raw_msg = 'sync:'

        self.assertRaises(BadWebiCommandException, self._interface_webi._parse_webi_command, raw_msg)

    def test_parse_webi_command_empty_type(self):
        raw_msg = ':dialplan reload'

        self.assertRaises(BadWebiCommandException, self._interface_webi._parse_webi_command, raw_msg)

    def test_parse_webi_command_only_separator(self):
        raw_msg = ':'

        self.assertRaises(BadWebiCommandException, self._interface_webi._parse_webi_command, raw_msg)

    def test_parse_webi_command_bad_type(self):
        raw_msg = 'notsync:dialplan reload'

        self.assertRaises(BadWebiCommandException, self._interface_webi._parse_webi_command, raw_msg)

    def test_parse_webi_command_bad_syntax(self):
        raw_msg = 'syncdialplan reload'

        self.assertRaises(BadWebiCommandException, self._interface_webi._parse_webi_command, raw_msg)

    def test_send_ami_request_sync(self):
        msg = 'sip show peer francis'
        type = 'sync'
        self._interface_webi.ipbxid = '1234'
        self._ctiserver.myami = Mock(AMI)

        result = self._interface_webi._send_ami_request(type, msg)

        self._ctiserver.myami.delayed_action.assert_called_once_with(msg, self._interface_webi)
        self.assertEqual(False, result)

    def test_send_ami_request_async(self):
        msg = 'dialplan reload'
        type = 'async'
        self._interface_webi.ipbxid = '1234'
        self._ctiserver.myami = Mock(AMI)

        result = self._interface_webi._send_ami_request(type, msg)

        self._ctiserver.myami.delayed_action.assert_called_once_with(msg)
        self.assertEqual(True, result)

    def test_manage_connection_reload_daemon(self):
        raw_msg = 'async:xivo[daemon,reload]'
        expected_result = [{'message': [],
                            'closemenow': True}]
        self._interface_webi._parse_webi_command = Mock()
        self._interface_webi._parse_webi_command.return_value = ('async', 'xivo[daemon,reload]')

        result = self._interface_webi.manage_connection(raw_msg)

        self.assertEqual(self._ctiserver.askedtoquit, True)
        self.assertEqual(expected_result, result)

    def test_manage_connection_queuemember_update(self):
        raw_msg = 'async:xivo[queuemember,update]'
        expected_result = [{'message': [],
                            'closemenow': True}]
        self._interface_webi._parse_webi_command = Mock()
        self._interface_webi.queuemember_service_manager = Mock(QueueMemberServiceManager)
        self._interface_webi._parse_webi_command.return_value = ('async', 'xivo[queuemember,update]')

        result = self._interface_webi.manage_connection(raw_msg)

        self._interface_webi.queuemember_service_manager.update_config.assert_called_once_with()
        self.assertEqual(expected_result, result)

    def test_manage_connection_update_request(self):
        raw_msg = 'async:xivo[userlist,update]'
        expected_result = [{'message': [],
                            'closemenow': True}]
        self._interface_webi.ipbxid = '1234'
        self._interface_webi._ctiserver.update_userlist = Mock()
        self._interface_webi._parse_webi_command = Mock()
        self._interface_webi._parse_webi_command.return_value = ('async', 'xivo[userlist,update]')

        result = self._interface_webi.manage_connection(raw_msg)

        self._interface_webi._ctiserver.update_userlist.append.assert_called_once_with('xivo[userlist,update]')
        self.assertEqual(expected_result, result)

    def test_manage_connection_async_ami_request(self):
        raw_msg = 'async:sip reload'
        expected_result = [{'message': [],
                            'closemenow': False}]
        self._interface_webi.ipbxid = '1234'
        self._interface_webi._parse_webi_command = Mock()
        self._interface_webi._parse_webi_command.return_value = ('async', 'sip reload')
        self._interface_webi._send_ami_request = Mock()
        self._interface_webi._send_ami_request.return_value = False

        result = self._interface_webi.manage_connection(raw_msg)

        self._interface_webi._send_ami_request.assert_called_once_with('async', 'sip reload')
        self.assertEqual(expected_result, result)

    def test_manage_connection_sip_show_peer(self):
        raw_msg = 'async:sip show peer francis'
        expected_result = [{'message': [],
                            'closemenow': False}]
        self._interface_webi.ipbxid = '1234'
        self._interface_webi._parse_webi_command = Mock()
        self._interface_webi._parse_webi_command.return_value = ('sync', 'sip show peer francis')
        self._interface_webi._send_ami_request = Mock()
        self._interface_webi._send_ami_request.return_value = False

        result = self._interface_webi.manage_connection(raw_msg)

        self._interface_webi._send_ami_request.assert_called_once_with('sync', 'sip show peer francis')
        self.assertEqual(expected_result, result)

    def test_manage_connection_unknown_msg(self):
        raw_msg = 'async:command that does_not exist'
        expected_result = [{'message': [],
                            'closemenow': True}]
        self._interface_webi.ipbxid = '1234'
        self._interface_webi._parse_webi_command = Mock()
        self._interface_webi._parse_webi_command.return_value = ('async', 'command that does_not exist')
        self._interface_webi._send_ami_request = Mock()

        result = self._interface_webi.manage_connection(raw_msg)

        self._interface_webi._parse_webi_command.assert_called_once_with(raw_msg)
        self._interface_webi._send_ami_request.assert_never_called()
        self.assertEqual(expected_result, result)

    def test_manage_connection_live_reload_disable(self):
        raw_msg = 'async:sip reload'
        expected_result = [{'message': [],
                            'closemenow': True}]
        self._interface_webi._config.getconfig.return_value = {'live_reload_conf': False}
        self._interface_webi._parse_webi_command = Mock()
        self._interface_webi._send_ami_request = Mock()

        result = self._interface_webi.manage_connection(raw_msg)

        self._interface_webi._parse_webi_command.assert_never_called()
        self._interface_webi._send_ami_request.assert_never_called()
        self.assertEqual(expected_result, result)

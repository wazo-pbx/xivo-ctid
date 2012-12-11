# -*- coding: UTF-8 -*-

import unittest

from xivo_cti.xivo_ami import AMIClass
from mock import Mock
from xivo_cti.cti_config import Config


class TestXivoAMI(unittest.TestCase):

    def setUp(self):
        ipbxconfig = {
            'ipbx_connection': {
                'ipaddress': '127.0.0.1',
                'ipport': 5038,
                'loginname': 'xivouser',
                'password': 'xivouser'
            }
        }
        config = Mock(Config)
        config.getconfig.return_value = ipbxconfig
        ami_class = AMIClass(config)
        ami_class._exec_command = Mock()
        self.ami_class = ami_class

    def testSIPNotify_with_variables(self):
        channel = 'SIP/1234'
        variables = {'Event': 'val',
                     'Deux': 'val2',
                     'Trois': 3}

        self.ami_class.sipnotify(channel, variables)

        excpected_var = ['SIPNotify', sorted([('Channel', channel),
                                              ('Variable', 'Event=val'),
                                              ('Variable', 'Deux=val2'),
                                              ('Variable', 'Trois=3')])]
        result = list(self.ami_class._exec_command.call_args_list[0][0])
        result[1] = sorted(result[1])
        self.assertEquals(result, excpected_var)

    def testSIPNotify_missing_fields(self):
        self.assertRaises(ValueError, self.ami_class.sipnotify, 'SIP/abc', {})
        self.assertRaises(ValueError, self.ami_class.sipnotify, None, {'Event': 'aastra-xml'})

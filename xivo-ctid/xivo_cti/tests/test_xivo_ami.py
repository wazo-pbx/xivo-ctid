# -*- coding: UTF-8 -*-

import unittest

from xivo_cti.xivo_ami import AMIClass
from mock import Mock


class TestXivoAMI(unittest.TestCase):

    def testSIPNotify_with_variables(self):
        channel = 'SIP/1234'
        variables = {'Event': 'val',
                     'Deux': 'val2',
                     'Trois': 3}

        ami_class = AMIClass('xivo', 'localhost', 5038, 'uname', 'password', True)
        ami_class._exec_command = Mock()

        ami_class.sipnotify(channel, variables)

        excpected_var = ['SIPNotify', sorted([('Channel', channel),
                                              ('Variable', 'Event=val'),
                                              ('Variable', 'Deux=val2'),
                                              ('Variable', 'Trois=3')])]
        result = list(ami_class._exec_command.call_args_list[0][0])
        result[1] = sorted(result[1])
        self.assertEquals(result, excpected_var)

    def testSIPNotify_missing_fields(self):
        ami_class = AMIClass('xivo', 'localhost', 5038, 'uname', 'password', True)
        ami_class._exec_command = Mock()

        self.assertRaises(ValueError, ami_class.sipnotify, 'SIP/abc', {})
        self.assertRaises(ValueError, ami_class.sipnotify, None, {'Event': 'aastra-xml'})

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

from xivo_cti.xivo_ami import AMIClass
from mock import Mock
from mock import sentinel
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

    def test_switchboard_retrieve(self):
        line_interface = sentinel.line_interface
        channel = 'SIP/abcd-1234'
        cid_name = 'Alice'
        cid_num = '555'

        self.ami_class.switchboard_retrieve(line_interface, channel, cid_name, cid_num)

        self.ami_class._exec_command.assert_called_once_with(
            'Originate',
            [('Channel', line_interface),
             ('Exten', 's'),
             ('Context', 'xivo_switchboard_retrieve'),
             ('Priority', '1'),
             ('Variable', 'XIVO_CID_NUM=%s' % cid_num),
             ('Variable', 'XIVO_CID_NAME=%s' % cid_name),
             ('Variable', 'XIVO_CHANNEL=%s' % channel),
             ('Async', 'true')])

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

    def test_hangup(self):
        channel = sentinel.channel_to_hangup
        self.ami_class.hangup(channel)

        self.ami_class._exec_command.assert_called_once_with(
            'Hangup', [('Channel', channel)])

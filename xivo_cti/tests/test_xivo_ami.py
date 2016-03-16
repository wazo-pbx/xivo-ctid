# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
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

from collections import Counter

from xivo_cti.xivo_ami import AMIClass
from mock import Mock
from mock import patch
from mock import sentinel


class TestXivoAMI(unittest.TestCase):

    def setUp(self):
        with patch('xivo_cti.xivo_ami.config', {'ami': {}}):
            ami_class = AMIClass()
        ami_class._exec_command = Mock()
        self.ami_class = ami_class

    @staticmethod
    def _list_match_anyorder(left, right):
        return Counter(left) == Counter(right)

    def _assert_exec_command(self, cmd, args):
        for call in self.ami_class._exec_command.call_args_list:
            called_cmd, called_args = call[0]
            if called_cmd != cmd:
                continue
            if self._list_match_anyorder(called_args, args):
                return

        self.fail('No call matched "{}" with args {} in:\n{}'.format(
            cmd, args, self.ami_class._exec_command.call_args_list))

    def test_hangup(self):
        channel = sentinel.channel_to_hangup

        self.ami_class.hangup(channel)

        self._assert_exec_command('Hangup', [('Channel', channel)])

    def test_hangup_with_cause_answered_elsewhere(self):
        channel = sentinel.channel_to_hangup

        self.ami_class.hangup_with_cause_answered_elsewhere(channel)

        self._assert_exec_command('Hangup', [('Channel', channel), ('Cause', '26')])

    def test_redirect(self):
        channel, context, extension, priority = 'channel', 'ctx', '1001', '2'

        self.ami_class.redirect(channel, context, extension, priority)

        self._assert_exec_command('Redirect',
                                  [('Channel', channel),
                                   ('Context', context),
                                   ('Exten', extension),
                                   ('Priority', priority)])

    def test_switchboard_retrieve(self):
        line_interface = sentinel.line_interface
        channel = 'SIP/abcd-1234'
        cid_name = 'Alice'
        cid_num = '555'
        cid_name_src = 'Bob'
        cid_num_src = '444'

        self.ami_class.switchboard_retrieve(line_interface, channel, cid_name, cid_num, cid_name_src, cid_num_src)

        self._assert_exec_command('Originate',
                                  [('Channel', line_interface),
                                   ('Exten', 's'),
                                   ('Context', 'xivo_switchboard_retrieve'),
                                   ('Priority', '1'),
                                   ('CallerID', '"%s" <%s>' % (cid_name, cid_num)),
                                   ('Variable', 'XIVO_CID_NUM=%s' % cid_num),
                                   ('Variable', 'XIVO_CID_NAME=%s' % cid_name),
                                   ('Variable', 'XIVO_ORIG_CID_NUM=%s' % cid_num_src),
                                   ('Variable', 'XIVO_ORIG_CID_NAME=%s' % cid_name_src),
                                   ('Variable', 'XIVO_CHANNEL=%s' % channel),
                                   ('Async', 'true')])

    def testSIPNotify_with_variables(self):
        channel = 'SIP/1234'
        variables = {'Event': 'val',
                     'Deux': 'val2',
                     'Trois': 3}

        self.ami_class.sipnotify(channel, variables)

        self._assert_exec_command('SIPNotify', [('Channel', channel),
                                                ('Variable', 'Event=val'),
                                                ('Variable', 'Deux=val2'),
                                                ('Variable', 'Trois=3')])

    def testSIPNotify_missing_fields(self):
        self.assertRaises(ValueError, self.ami_class.sipnotify, 'SIP/abc', {})
        self.assertRaises(ValueError, self.ami_class.sipnotify, None, {'Event': 'aastra-xml'})

    def test_voicemail_atxfer(self):
        channel, context, voicemail_number = 'chan', 'ctx', '1002'
        call_voicemail_exten = '_*97665XXXX'

        with patch('xivo_cti.xivo_ami.extensions_dao.exten_by_name', Mock(return_value=call_voicemail_exten)):
            self.ami_class.voicemail_atxfer(channel, context, voicemail_number)

        self._assert_exec_command('Atxfer', [('Channel', channel),
                                             ('Context', context),
                                             ('Exten', '*976651002#'),
                                             ('Priority', '1')])

    def test_voicemail_transfer(self):
        channel, context, voicemail_number = 'chan', 'ctx', '1002'

        self.ami_class.voicemail_transfer(channel, context, voicemail_number)

        self._assert_exec_command('Setvar', [('Variable', 'XIVO_BASE_CONTEXT'),
                                             ('Value', context),
                                             ('Channel', channel)])
        self._assert_exec_command('Setvar', [('Variable', 'ARG1'),
                                             ('Value', voicemail_number),
                                             ('Channel', channel)])
        self._assert_exec_command('Redirect', [('Channel', channel),
                                               ('Context', 'vmbox'),
                                               ('Exten', 's'),
                                               ('Priority', '1')])

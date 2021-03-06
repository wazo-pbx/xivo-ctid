# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from collections import Counter

from xivo_cti.xivo_ami import AMIClass
from mock import (
    Mock,
    patch,
    sentinel,
)


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

        self.ami_class.switchboard_retrieve(
            line_interface,
            channel,
            cid_name,
            cid_num,
            cid_name_src,
            cid_num_src,
        )

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
        channel = 'PJSIP/1234'
        variables = {
            'Event': 'val',
            'Deux': 'val2',
            'Trois': 3,
        }

        self.ami_class.sipnotify(channel, variables)

        self._assert_exec_command(
            'PJSIPNotify',
            [
                ('Endpoint', channel),
                ('Variable', 'Event=val'),
                ('Variable', 'Deux=val2'),
                ('Variable', 'Trois=3'),
            ]
        )

    def testSIPNotify_missing_fields(self):
        self.assertRaises(ValueError, self.ami_class.sipnotify, 'SIP/abc', {})
        self.assertRaises(ValueError, self.ami_class.sipnotify, None, {'Event': 'aastra-xml'})

# -*- coding: utf-8 -*-

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from xivo_cti.services.funckey.manager import FunckeyManager
from xivo import xivo_helpers
from xivo_cti.xivo_ami import AMIClass
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.alchemy.extension import Extension
from mock import patch, Mock


class TestFunckeyManager(DAOTestCase):

    tables = [PhoneFunckey, Extension]

    def setUp(self):
        self.user_id = 123
        ami_class = Mock(AMIClass)
        self.manager = FunckeyManager(ami_class)
        xivo_helpers.fkey_extension = Mock()
        self.ami = Mock(AMIClass)
        self.manager.ami = self.ami

    @patch('xivo_dao.extensions_dao.exten_by_name', Mock(return_value='*735'))
    def test_dnd_in_use(self):
        xivo_helpers.fkey_extension.return_value = '*735123***225'

        self.manager.dnd_in_use(self.user_id, True)

        self.manager.ami.sendcommand.assert_called_once_with(
            'Command', [('Command', 'devstate change Custom:*735123***225 INUSE')]
        )

    @patch('xivo_dao.extensions_dao.exten_by_name', Mock(return_value='*735'))
    def test_dnd_not_in_use(self):
        xivo_helpers.fkey_extension.return_value = '*735123***225'

        self.manager.dnd_in_use(self.user_id, False)

        self.manager.ami.sendcommand.assert_called_once_with(
            'Command', [('Command', 'devstate change Custom:*735123***225 NOT_INUSE')]
        )

    @patch('xivo_dao.extensions_dao.exten_by_name', Mock(return_value='*735'))
    def test_call_filter_in_use(self):
        xivo_helpers.fkey_extension.return_value = '*735123***227'

        self.manager.call_filter_in_use(self.user_id, True)

        self.manager.ami.sendcommand.assert_called_once_with(
            'Command', [('Command', 'devstate change Custom:*735123***227 INUSE')]
        )

    @patch('xivo_dao.extensions_dao.exten_by_name', Mock(return_value='*735'))
    def test_call_filter_not_in_use(self):
        xivo_helpers.fkey_extension.return_value = '*735123***227'

        self.manager.call_filter_in_use(self.user_id, False)

        self.manager.ami.sendcommand.assert_called_once_with(
            'Command', [('Command', 'devstate change Custom:*735123***227 NOT_INUSE')]
        )

    @patch('xivo_dao.extensions_dao.exten_by_name', Mock(return_value='*735'))
    def test_fwd_unc_in_use(self):
        destination = '1002'

        def fkey_exten(prefix, args):
            if args[2]:
                return '*735123***221*%s' % args[2]
            else:
                return '*735123***221'

        xivo_helpers.fkey_extension.side_effect = fkey_exten

        self.manager.unconditional_fwd_in_use(self.user_id, destination, True)

        expected_calls = [
            (('Command', [('Command', 'devstate change Custom:*735123***221*1002 INUSE')]), {}),
            (('Command', [('Command', 'devstate change Custom:*735123***221 INUSE')]), {}),
        ]

        calls = self.manager.ami.sendcommand.call_args_list

        expected_calls = sorted(expected_calls)
        calls = sorted(calls)

        self.assertEqual(calls, expected_calls)

    @patch('xivo_dao.extensions_dao.exten_by_name', Mock(return_value='*735'))
    def test_fwd_unc_not_in_use(self):
        destination = '1003'

        def fkey_exten(prefix, args):
            if args[2]:
                return '*735123***221*%s' % args[2]
            else:
                return '*735123***221'

        xivo_helpers.fkey_extension.side_effect = fkey_exten

        self.manager.unconditional_fwd_in_use(self.user_id, destination, False)

        expected_calls = [
            (('Command', [('Command', 'devstate change Custom:*735123***221*1003 NOT_INUSE')]), {}),
            (('Command', [('Command', 'devstate change Custom:*735123***221 NOT_INUSE')]), {}),
        ]

        calls = self.manager.ami.sendcommand.call_args_list

        expected_calls = sorted(expected_calls)
        calls = sorted(calls)

        self.assertEqual(calls, expected_calls)

    @patch('xivo_dao.phonefunckey_dao.get_dest_unc')
    def test_disable_all_fwd_unc(self, mock_get_dest_unc):
        unc_dest = ['123', '666', '', '012']
        fn = Mock()
        self.manager.unconditional_fwd_in_use = fn
        mock_get_dest_unc.return_value = unc_dest

        self.manager.disable_all_unconditional_fwd(self.user_id)

        for dest in unc_dest:
            if dest:
                self.assertEqual(fn.call_count, 3)

    @patch('xivo_dao.phonefunckey_dao.get_dest_rna')
    def test_disable_all_fwd_rna(self, mock_get_dest_rna):
        rna_dest = ['123', '666', '', '012']
        fn = Mock()
        self.manager.rna_fwd_in_use = fn
        mock_get_dest_rna.return_value = rna_dest

        self.manager.disable_all_rna_fwd(self.user_id)

        for dest in rna_dest:
            if dest:
                self.assertEqual(fn.call_count, 3)

    @patch('xivo_dao.phonefunckey_dao.get_dest_busy')
    def test_disable_all_fwd_busy(self, mock_get_dest_busy):
        busy_dest = ['123', '666', '', '012']
        fn = Mock()
        self.manager.busy_fwd_in_use = fn
        mock_get_dest_busy.return_value = busy_dest

        self.manager.disable_all_busy_fwd(self.user_id)

        for dest in busy_dest:
            if dest:
                self.assertEqual(fn.call_count, 3)

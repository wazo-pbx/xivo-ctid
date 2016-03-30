# -*- coding: utf-8 -*-

# Copyright (C) 2007-2016 Avencall
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

from xivo_cti.services.funckey.manager import FunckeyManager
from xivo import xivo_helpers
from xivo_cti.xivo_ami import AMIClass
from xivo_cti.dao.forward_dao import ForwardDAO
from mock import call, patch, Mock
import unittest


class TestFunckeyManager(unittest.TestCase):

    def setUp(self):
        xivo_helpers.fkey_extension = Mock()

        self.user_id = 123
        self.forward_dao = Mock(ForwardDAO)
        self.dao = Mock(forward=self.forward_dao)
        self.ami = Mock(AMIClass)

        self.manager = FunckeyManager(self.ami)
        self.manager.dao = self.dao

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
        xivo_helpers.fkey_extension.return_value = '*735123***221*{}'.format(destination)

        self.manager.unconditional_fwd_in_use(self.user_id, destination, True)

        self.manager.ami.sendcommand.assert_called_once_with(
            'Command', [('Command', 'devstate change Custom:*735123***221*1002 INUSE')])

    @patch('xivo_dao.extensions_dao.exten_by_name', Mock(return_value='*735'))
    def test_fwd_unc_not_in_use(self):
        destination = '1003'
        xivo_helpers.fkey_extension.return_value = '*735123***221*{}'.format(destination)

        self.manager.unconditional_fwd_in_use(self.user_id, destination, False)

        self.manager.ami.sendcommand.assert_called_once_with(
            'Command', [('Command', 'devstate change Custom:*735123***221*1003 NOT_INUSE')])

    def test_update_all_unconditional_fwd(self):
        unc_dest = ['123', '666', '', '0123']
        enabled = True
        destination = '123'
        fn = Mock()
        self.manager.unconditional_fwd_in_use = fn
        self.forward_dao.unc_destinations.return_value = unc_dest

        self.manager.update_all_unconditional_fwd(self.user_id, enabled, destination)
        self.forward_dao.unc_destinations.assert_called_once_with(self.user_id)
        expected_calls = [
            call(self.user_id, '123', True),
            call(self.user_id, '666', False),
            call(self.user_id, '', True),
            call(self.user_id, '0123', False),
        ]
        fn.assert_has_calls(expected_calls)
        self.assertEqual(fn.call_count, 4)

    def test_update_all_rna_fwd(self):
        rna_dest = ['123', '666', '', '0123']
        enabled = True
        destination = '123'
        fn = Mock()
        self.manager.rna_fwd_in_use = fn
        self.forward_dao.rna_destinations.return_value = rna_dest

        self.manager.update_all_rna_fwd(self.user_id, enabled, destination)
        self.forward_dao.rna_destinations.assert_called_once_with(self.user_id)
        expected_calls = [
            call(self.user_id, '123', True),
            call(self.user_id, '666', False),
            call(self.user_id, '', True),
            call(self.user_id, '0123', False),
        ]
        fn.assert_has_calls(expected_calls)
        self.assertEqual(fn.call_count, 4)

    def test_update_all_busy_fwd(self):
        busy_dest = ['123', '666', '', '0123']
        enabled = True
        destination = '123'
        fn = Mock()
        self.manager.busy_fwd_in_use = fn
        self.forward_dao.busy_destinations.return_value = busy_dest

        self.manager.update_all_busy_fwd(self.user_id, enabled, destination)
        self.forward_dao.busy_destinations.assert_called_once_with(self.user_id)
        expected_calls = [
            call(self.user_id, '123', True),
            call(self.user_id, '666', False),
            call(self.user_id, '', True),
            call(self.user_id, '0123', False),
        ]
        fn.assert_has_calls(expected_calls)
        self.assertEqual(fn.call_count, 4)

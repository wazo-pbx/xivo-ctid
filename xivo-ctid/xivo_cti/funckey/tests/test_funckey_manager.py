#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2011  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
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

import unittest

from xivo_cti.funckey.funckey_manager import FunckeyManager
from tests.mock import Mock
from xivo_cti.dao.extensionsdao import ExtensionsDAO
from xivo import xivo_helpers
from xivo_cti.xivo_ami import AMIClass


class TestFunckeyManager(unittest.TestCase):

    def setUp(self):
        self.user_id = 123
        self.manager = FunckeyManager()
        self.manager.extensionsdao = Mock(ExtensionsDAO)
        xivo_helpers.fkey_extension = Mock()
        self.ami = Mock(AMIClass)
        self.manager.ami = self.ami

        self._funckey_exten = '_*735'
        self._enablednd_exten = '*25'

    def tearDown(self):
        pass

    def test_dnd_in_use(self):
        xivo_helpers.fkey_extension.return_value = '*735123***225'
        self.manager.dnd_in_use(self.user_id)

        self.manager.extensionsdao.exten_by_name = lambda x: self._funckey_exten if x == 'phoneprogfunckey' else self._enablednd_exten

        self.manager.ami.sendcommand.assert_called_once_with('Command', [('Command', 'devstate change Custom:*735123***225 INUSE')])

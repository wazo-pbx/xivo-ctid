# vim: set fileencoding=utf-8 :
# XiVO CTI Server

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

from xivo_cti.cti.cti_command_factory import CTICommandFactory
from xivo_cti.cti.commands.invite_confroom import InviteConfroom


class Test(unittest.TestCase):

    def setUp(self):
        self._msg_1 = {'class': 'invite_confroom',
                       'commandid': 737000717,
                       'invitee': 'user:pcmdev/3'}

    def tearDown(self):
        pass

    def test_cti_command_factory(self):
        factory = CTICommandFactory()

        self.assertTrue(factory is not None)

    def test_get_command(self):
        factory = CTICommandFactory()

        commands = factory.get_command(self._msg_1)

        self.assertTrue(InviteConfroom in commands)

    def test_register_class(self):
        CTICommandFactory.register_class(InviteConfroom)

        self.assertTrue(InviteConfroom in CTICommandFactory._registered_classes)


if __name__ == "__main__":
    unittest.main()

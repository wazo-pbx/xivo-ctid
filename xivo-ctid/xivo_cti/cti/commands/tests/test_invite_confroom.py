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

from xivo_cti.cti.missing_field_exception import MissingFieldException
from xivo_cti.cti.commands.invite_confroom import InviteConfroom


class Test(unittest.TestCase):

    def setUp(self):
        self.command_class = 'invite_confroom'

    def tearDown(self):
        pass

    def test_invite_confroom(self):
        self.assertEqual(len(InviteConfroom.required_fields), 2)
        self.assertTrue('class' in InviteConfroom.required_fields)
        self.assertTrue('invitee' in InviteConfroom.required_fields)

        try:
            InviteConfroom.from_dict({'class': self.command_class})
            self.assertTrue(False, u'Should raise an exception')
        except MissingFieldException:
            self.assertTrue(True, u'Should raise an exception')

        invitee = 'user:myxivo/123'
        command = InviteConfroom.from_dict({'class': self.command_class, 'invitee': invitee})
        self.assertEqual(command.command_class, self.command_class)
        self.assertEqual(command._invitee, invitee)

    def test_match_message(self):
        self.assertFalse(InviteConfroom.match_message({}))
        self.assertFalse(InviteConfroom.match_message({'class': 'invite_confroom*'}))
        self.assertTrue(InviteConfroom.match_message({'class': 'invite_confroom'}))

# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

from xivo_cti.cti.commands.invite_confroom import InviteConfroom


class Test(unittest.TestCase):

    def setUp(self):
        self.command_class = 'invite_confroom'

    def test_invite_confroom(self):
        try:
            InviteConfroom.from_dict({'class': self.command_class})
            self.assertTrue(False, u'Should raise an exception')
        except KeyError:
            self.assertTrue(True, u'Should raise an exception')

        invitee = 'user:myxivo/123'
        command = InviteConfroom.from_dict({'class': self.command_class, 'invitee': invitee})
        self.assertEqual(command.command_class, self.command_class)
        self.assertEqual(command.invitee, invitee)

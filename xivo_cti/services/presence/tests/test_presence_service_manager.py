# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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
from mock import Mock
from xivo_cti.services.presence.manager import PresenceServiceManager
from xivo_cti.dao.innerdata_dao import InnerdataDAO


class TestPresenceServiceManager(unittest.TestCase):

    def setUp(self):
        self.presence_manager = PresenceServiceManager()
        self.presence_manager.dao.innerdata = Mock(InnerdataDAO)

    def tearDown(self):
        pass

    def test_is_valid_presence_yes(self):
        profile = 'client'
        presence = 'disconnected'

        self.presence_manager.dao.innerdata.get_presences.return_value = ['available', 'disconnected']

        result = self.presence_manager.is_valid_presence(profile, presence)

        self.presence_manager.dao.innerdata.get_presences.assert_called_once_with(profile)
        self.assertTrue(result)

    def test_is_valid_presence_no(self):
        profile = 'client'
        presence = 'DnD'

        self.presence_manager.dao.innerdata.get_presences.return_value = ['available', 'disconnected']

        result = self.presence_manager.is_valid_presence(profile, presence)

        self.presence_manager.dao.innerdata.get_presences.assert_called_once_with(profile)
        self.assertFalse(result)

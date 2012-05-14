# -*- coding: utf-8 -*-

import unittest
from tests.mock import Mock
from xivo_cti.services.presence_service_manager import PresenceServiceManager
from xivo_cti.dao.innerdatadao import InnerdataDAO


class TestPresenceServiceManager(unittest.TestCase):
    def setUp(self):
        self.presence_manager = PresenceServiceManager()
        self.innerdata_dao = Mock(InnerdataDAO)
        self.presence_manager.innerdata_dao = self.innerdata_dao

    def tearDown(self):
        pass

    def test_is_valid_presence_yes(self):
        profile = 'client'
        presence = 'disconnected'

        self.innerdata_dao.get_presences.return_value = ['available', 'disconnected']

        result = self.presence_manager.is_valid_presence(profile, presence)

        self.presence_manager.innerdata_dao.get_presences.assert_called_once_with(profile)
        self.assertTrue(result)

    def test_is_valid_presence_no(self):
        profile = 'client'
        presence = 'DnD'

        self.innerdata_dao.get_presences.return_value = ['available', 'disconnected']

        result = self.presence_manager.is_valid_presence(profile, presence)

        self.presence_manager.innerdata_dao.get_presences.assert_called_once_with(profile)
        self.assertFalse(result)

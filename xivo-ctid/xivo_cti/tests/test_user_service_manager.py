import unittest

from xivo_cti.user_service_manager import UserServiceManager
from tests.mock import Mock
from xivo_cti.dao.userfeaturesdao import UserFeaturesDAO
from xivo_cti.services.user_service_notifier import UserServiceNotifier


class TestUserServiceManager(unittest.TestCase):

    def setUp(self):
        self.user_service_manager = UserServiceManager()
        self.user_features_dao = Mock(UserFeaturesDAO)
        self.user_service_manager.user_features_dao = self.user_features_dao
        self.user_service_notifier = Mock(UserServiceNotifier)
        self.user_service_manager.user_service_notifier = self.user_service_notifier

    def test_enable_dnd(self):
        user_id = 123

        self.user_service_manager.enable_dnd(user_id)

        self.user_features_dao.enable_dnd.assert_called_once_with(user_id)
        self.user_service_notifier.dnd_enabled.assert_called_once_with(user_id)


    def test_disable_dnd(self):

        user_id=241

        self.user_service_manager.disable_dnd(user_id)

        self.user_features_dao.disable_dnd.assert_called_once_with(user_id)
        self.user_service_notifier.dnd_disabled.assert_called_once_with(user_id)


    def test_enable_filter(self):
        user_id = 789

        self.user_service_manager.enable_filter(user_id)

        self.user_features_dao.enable_filter.assert_called_once_with(user_id)
        self.user_service_notifier.filter_enabled.assert_called_once_with(user_id)


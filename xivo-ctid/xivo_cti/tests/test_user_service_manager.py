import unittest

from xivo_cti.user_service_manager import UserServiceManager
from tests.mock import Mock
from xivo_cti.dao.userfeaturesdao import UserFeaturesDAO
from xivo_cti.services.user_service_notifier import UserServiceNotifier


class TestUserServiceManager(unittest.TestCase):

    def test_enable_dnd(self):
        user_id = 123
        user_service_manager = UserServiceManager()
        user_features_dao = Mock(UserFeaturesDAO)
        user_service_manager.user_features_dao = user_features_dao
        user_service_notifier = Mock(UserServiceNotifier)
        user_service_manager.user_service_notifier = user_service_notifier

        user_service_manager.enable_dnd(user_id)

        user_features_dao.enable_dnd.assert_called_once_with(user_id)
        user_service_notifier.dnd_enabled.assert_called_once_with(user_id)

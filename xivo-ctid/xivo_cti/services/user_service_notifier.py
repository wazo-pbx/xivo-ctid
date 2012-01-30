import logging

logger = logging.getLogger('user_service_notifier')


class UserServiceNotifier(object):

    def dnd_enabled(self, user_id):
        self.events_cti.put({"class": "getlist",
                             "config": {"enablednd": True},
                             "function": "updateconfig",
                             "listname": "users",
                             "tid": user_id,
                             "tipbxid": self.ipbx_id})

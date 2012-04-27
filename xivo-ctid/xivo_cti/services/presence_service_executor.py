# -*- coding: UTF-8 -*-

class PresenceServiceExecutor(object):
    def execute_actions(self, user_id, presence):
        self._innerdata.presence_action(user_id)

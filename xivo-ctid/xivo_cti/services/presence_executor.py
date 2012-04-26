# -*- coding: UTF-8 -*-

class PresenceExecutor(object):
    def disconnect(self, user_id):
        self._innerdata.presence_action(user_id)

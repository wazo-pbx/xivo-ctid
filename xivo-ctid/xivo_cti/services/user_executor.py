# -*- coding: UTF-8 -*-

class UserExecutor(object):
    def notify_cti(self, user_id):
        self._innerdata.handle_cti_stack('set', ('users', 'updatestatus', user_id))
        self._innerdata.handle_cti_stack('empty_stack')

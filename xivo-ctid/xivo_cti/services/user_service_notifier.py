import logging

logger = logging.getLogger('user_service_notifier')


class UserServiceNotifier(object):

    DND_MESSAGE = {"class": "getlist",
                   "config": {"enablednd": True},
                   "function": "updateconfig",
                   "listname": "users",
                   "tid": '',
                   "tipbxid": ''}


    def _prepare_dnd_message(self,dnd_status,user_id):
        dnd_enabled_msg = self.DND_MESSAGE
        dnd_enabled_msg['config']['enablednd'] = dnd_status
        dnd_enabled_msg['tid'] = user_id
        dnd_enabled_msg['tipbxid'] = self.ipbx_id
        return dnd_enabled_msg

    def dnd_enabled(self, user_id):

        self.events_cti.put(self._prepare_dnd_message(True,user_id))



    def dnd_disabled(self, user_id):

        self.events_cti.put(self._prepare_dnd_message(False,user_id))

import logging
from copy import deepcopy

logger = logging.getLogger('user_service_notifier')


class UserServiceNotifier(object):

    STATUS_MESSAGE = {"class": "getlist",
                   "function": "updateconfig",
                   "listname": "users",
                   "tid": '',
                   "tipbxid": ''}

    def _prepare_message(self, user_id):
        msg = deepcopy(self.STATUS_MESSAGE)
        msg.update({'tid': user_id,
                    'tipbxid': self.ipbx_id})
        return msg

    def _prepare_dnd_message(self, dnd_status, user_id):
        dnd_enabled_msg = self._prepare_message(user_id)
        dnd_enabled_msg['config'] = {'enablednd': dnd_status}
        return dnd_enabled_msg

    def _prepare_filter_message(self, filter_status, user_id):
        filter_status_msg = self._prepare_message(user_id)
        filter_status_msg['config'] = {'incallfilter': filter_status}
        return filter_status_msg

    def _prepare_unconditional_fwd_message(self, status, destination, user_id):
        filter_status_msg = self._prepare_message(user_id)
        filter_status_msg.update({'config': {'enableunc': status,
                                             'destunc': destination}})
        return filter_status_msg

    def _prepare_rna_fwd_message(self, status, destination, user_id):
        filter_status_msg = self._prepare_message(user_id)
        filter_status_msg.update({'config': {'enablerna': status,
                                             'destrna': destination}})
        return filter_status_msg

    def _prepare_busy_fwd_message(self, status, destination, user_id):
        filter_status_msg = self._prepare_message(user_id)
        filter_status_msg.update({'config': {'enablebusy': status,
                                             'destbusy': destination}})
        return filter_status_msg

    def dnd_enabled(self, user_id):
        self.events_cti.put(self._prepare_dnd_message(True, user_id))

    def dnd_disabled(self, user_id):
        self.events_cti.put(self._prepare_dnd_message(False, user_id))

    def filter_enabled(self, user_id):
        self.events_cti.put(self._prepare_filter_message(True, user_id))

    def filter_disabled(self, user_id):
        self.events_cti.put(self._prepare_filter_message(False, user_id))

    def unconditional_fwd_enabled(self, user_id, destination):
        self.events_cti.put(self._prepare_unconditional_fwd_message(True, destination, user_id))

    def unconditional_fwd_disabled(self, user_id, destination):
        self.events_cti.put(self._prepare_unconditional_fwd_message(False, destination, user_id))

    def rna_fwd_enabled(self, user_id, destination):
        self.events_cti.put(self._prepare_rna_fwd_message(True, destination, user_id))

    def rna_fwd_disabled(self, user_id, destination):
        self.events_cti.put(self._prepare_rna_fwd_message(False, destination, user_id))

    def busy_fwd_enabled(self, user_id, destination):
        self.events_cti.put(self._prepare_busy_fwd_message(True, destination, user_id))

    def busy_fwd_disabled(self, user_id, destination):
        self.events_cti.put(self._prepare_busy_fwd_message(False, destination, user_id))

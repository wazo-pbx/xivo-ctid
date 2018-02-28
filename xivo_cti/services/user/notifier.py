# -*- coding: utf-8 -*-
# Copyright (C) 2007-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

logger = logging.getLogger('user_service_notifier')


class UserServiceNotifier(object):

    def dnd_enabled(self, user_id, enabled):
        self.send_cti_event(self._prepare_dnd_message(enabled, user_id))

    def incallfilter_enabled(self, user_id, enabled):
        self.send_cti_event(self._prepare_filter_message(enabled, user_id))

    def unconditional_fwd_enabled(self, user_id, enabled, destination):
        self.send_cti_event(self._prepare_unconditional_fwd_message(enabled, destination, user_id))

    def rna_fwd_enabled(self, user_id, enabled, destination):
        self.send_cti_event(self._prepare_rna_fwd_message(enabled, destination, user_id))

    def busy_fwd_enabled(self, user_id, enabled, destination):
        self.send_cti_event(self._prepare_busy_fwd_message(enabled, destination, user_id))

    def presence_updated(self, user_id, presence):
        self.send_cti_event(self._prepare_presence_updated(user_id, presence))

    def recording_enabled(self, user_id):
        self.send_cti_event(self._prepare_recording_message(True, user_id))

    def recording_disabled(self, user_id):
        self.send_cti_event(self._prepare_recording_message(False, user_id))

    def _prepare_message(self, user_id):
        return {
            'class': 'getlist',
            'function': 'updateconfig',
            'listname': 'users',
            'tid': user_id,
            'tipbxid': self.ipbx_id,
        }

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

    def _prepare_presence_updated(self, user_id, presence):
        filter_status_msg = self._prepare_message(user_id)
        status_update = {'function': 'updatestatus',
                         'status': {'availstate': presence}}
        filter_status_msg.update(status_update)
        return filter_status_msg

    def _prepare_recording_message(self, recording_status, user_id):
        recording_enabled_msg = self._prepare_message(user_id)
        recording_enabled_msg['config'] = {'enablerecording': recording_status}
        return recording_enabled_msg

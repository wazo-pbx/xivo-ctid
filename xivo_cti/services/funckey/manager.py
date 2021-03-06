# -*- coding: utf-8 -*-
# Copyright 2007-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo import xivo_helpers

from xivo_cti import dao

from xivo_dao.helpers.db_utils import session_scope
from xivo_dao import extensions_dao


class FunckeyManager(object):

    DEVICE_PATTERN = 'Custom:%s'
    INUSE = 'INUSE'
    NOT_INUSE = 'NOT_INUSE'

    def __init__(self, ami_class):
        self.ami = ami_class
        self.dao = dao

    def _device(self, user_id, name, destination=''):
        with session_scope():
            funckey_prefix = extensions_dao.exten_by_name('phoneprogfunckey')
            funckey_args = (user_id, extensions_dao.exten_by_name(name), destination)
            funckey_pattern = xivo_helpers.fkey_extension(funckey_prefix, funckey_args)

        hint = self.DEVICE_PATTERN % funckey_pattern

        return hint

    def _send(self, device, status):
        self.ami.sendcommand(
            'Command', [('Command', 'devstate change %s %s' % (device, self.INUSE if status else self.NOT_INUSE))]
        )

    def dnd_in_use(self, user_id, status):
        device = self._device(user_id, 'enablednd')
        self._send(device, status)

    def call_filter_in_use(self, user_id, status):
        device = self._device(user_id, 'incallfilter')
        self._send(device, status)

    def unconditional_fwd_in_use(self, user_id, destination, status):
        device = self._device(user_id, 'fwdunc', destination)
        self._send(device, status)

    def rna_fwd_in_use(self, user_id, destination, status):
        device = self._device(user_id, 'fwdrna', destination)
        self._send(device, status)

    def busy_fwd_in_use(self, user_id, destination, status):
        device = self._device(user_id, 'fwdbusy', destination)
        self._send(device, status)

    def update_all_unconditional_fwd(self, user_id, enabled, destination):
        for user_dest in self.dao.forward.unc_destinations(user_id):
            if user_dest == destination or user_dest == '':
                self.unconditional_fwd_in_use(user_id, user_dest, enabled)
            else:
                self.unconditional_fwd_in_use(user_id, user_dest, False)

    def update_all_rna_fwd(self, user_id, enabled, destination):
        for user_dest in self.dao.forward.rna_destinations(user_id):
            if user_dest == destination or user_dest == '':
                self.rna_fwd_in_use(user_id, user_dest, enabled)
            else:
                self.rna_fwd_in_use(user_id, user_dest, False)

    def update_all_busy_fwd(self, user_id, enabled, destination):
        for user_dest in self.dao.forward.busy_destinations(user_id):
            if user_dest == destination or user_dest == '':
                self.busy_fwd_in_use(user_id, user_dest, enabled)
            else:
                self.busy_fwd_in_use(user_id, user_dest, False)

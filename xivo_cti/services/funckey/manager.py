# -*- coding: utf-8 -*-

# Copyright (C) 2007-2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

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

    def disable_all_unconditional_fwd(self, user_id):
        for destination in self.dao.forward.unc_destinations(user_id):
            self.unconditional_fwd_in_use(user_id, destination, False)

    def disable_all_rna_fwd(self, user_id):
        for destination in self.dao.forward.rna_destinations(user_id):
            self.rna_fwd_in_use(user_id, destination, False)

    def disable_all_busy_fwd(self, user_id):
        for destination in self.dao.forward.busy_destinations(user_id):
            self.busy_fwd_in_use(user_id, destination, False)

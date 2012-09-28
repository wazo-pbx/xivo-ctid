# -*- coding: utf-8 -*-

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xivo import xivo_helpers
from xivo_cti.dao import userfeaturesdao


class FunckeyManager(object):

    DEVICE_PATTERN = 'Custom:%s'
    INUSE = 'INUSE'
    NOT_INUSE = 'NOT_INUSE'

    def _device(self, user_id, name, destination=''):
        return (
            self.DEVICE_PATTERN %
            xivo_helpers.fkey_extension(self.extensionsdao.exten_by_name('phoneprogfunckey'),
                                        (user_id, self.extensionsdao.exten_by_name(name), destination)))

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
        for destination in self.phone_funckey_dao.get_dest_unc(user_id):
            if destination:
                self.unconditional_fwd_in_use(user_id, destination, False)

    def disable_all_rna_fwd(self, user_id):
        for destination in self.phone_funckey_dao.get_dest_rna(user_id):
            if destination:
                self.rna_fwd_in_use(user_id, destination, False)

    def disable_all_busy_fwd(self, user_id):
        for destination in self.phone_funckey_dao.get_dest_busy(user_id):
            if destination:
                self.busy_fwd_in_use(user_id, destination, False)


def parse_update_user_config(manager, event):
    if 'config' in event and 'tid' in event:
        config = event['config']
        user_id = int(event['tid'])
        if 'enableunc' in config or 'destunc' in config:
            _set_fwd_unc_blf(manager, user_id)
        if 'enablerna' in config or 'destrna' in config:
            _set_fwd_rna_blf(manager, user_id)
        if 'enablebusy' in config or 'destbusy' in config:
            _set_fwd_busy_blf(manager, user_id)


def _set_fwd_busy_blf(manager, user_id):
    manager.disable_all_busy_fwd(user_id)
    manager.busy_fwd_in_use(user_id,
                            userfeaturesdao.get_dest_busy(user_id),
                            userfeaturesdao.get_fwd_busy(user_id))


def _set_fwd_rna_blf(manager, user_id):
    manager.disable_all_rna_fwd(user_id)
    manager.rna_fwd_in_use(user_id,
                           userfeaturesdao.get_dest_rna(user_id),
                           userfeaturesdao.get_fwd_rna(user_id))


def _set_fwd_unc_blf(manager, user_id):
    manager.disable_all_unconditional_fwd(user_id)
    manager.unconditional_fwd_in_use(user_id,
                                     userfeaturesdao.get_dest_unc(user_id),
                                     userfeaturesdao.get_fwd_unc(user_id))

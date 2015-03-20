# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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


class Device(object):

    def __init__(self, id_):
        self.id = id_
        self.ip = None
        self.plugin = None
        self.vendor = None
        self.options = None

    def is_switchboard(self):
        if self.plugin and 'switchboard' in self.plugin:
            return True

        return bool(self.options and self.options.get('switchboard'))

    @classmethod
    def new_from_provd_device(cls, provd_device):
        device = cls(provd_device['id'])
        device.ip = provd_device.get('ip')
        device.plugin = provd_device.get('plugin')
        device.vendor = provd_device.get('vendor')
        device.options = provd_device.get('options')
        return device

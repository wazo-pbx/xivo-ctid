# -*- coding: utf-8 -*-

# XiVO CTI Server

# Copyright (C) 2007-2012  Avencall'
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the souce tree
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

from xivo_cti.services.device.controller.aastra import AastraController
from xivo_dao import device_dao


class DeviceManager(object):

    def __init__(self, ami_class):
        self.ami = ami_class
        self.aastra_controller = AastraController()

    def answer(self, device_id):
        if self.is_supported_device(device_id):
            cmd = self.aastra_controller.answer(device_id)
            self.send_sipnotify(cmd)

    def is_supported_device(self, device_id):
        vendor, model = device_dao.get_vendor_model(device_id)
        return vendor == 'Aastra' and model in ['6757i', '6755i']

    def send_sipnotify(self, cmd):
        self.ami.sipnotify(*cmd)

# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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


from xivo_cti.services.device.controller.aastra import AastraController
from xivo_dao.data_handler.device import services as device_services
from xivo_dao.data_handler.exception import ElementNotExistsError


class DeviceManager(object):

    def __init__(self, ami_class):
        self.ami = ami_class
        self.aastra_controller = AastraController()

    def answer(self, device_id):
        if self.is_supported_device(device_id):
            cmd = self.aastra_controller.answer(device_id)
            self.send_sipnotify(cmd)

    def is_supported_device(self, device_id):
        try:
            device = device_services.get(device_id)
            return device.vendor == 'Aastra' and device.model in ['6731i', '6757i', '6755i']
        except ElementNotExistsError:
            return False

    def send_sipnotify(self, cmd):
        self.ami.sipnotify(*cmd)

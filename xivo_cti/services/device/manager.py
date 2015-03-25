# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
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
from xivo_cti.services.device.controller.base import BaseController
from xivo_cti.services.device.controller.snom import SnomController
from xivo_cti.services.device.controller.yealink import YealinkController


class DeviceManager(object):

    def __init__(self, ami_class, cti_provd_client):
        self._base_controller = BaseController(ami_class)
        self._aastra_controller = AastraController(ami_class)
        self._snom_controller = SnomController(ami_class)
        self._yealink_controller = YealinkController(ami_class)
        self._cti_provd_client = cti_provd_client

    def get_answer_fn(self, device_id):
        device = self._cti_provd_client.find_device(device_id)
        controller = self._get_controller(device)

        return lambda: controller.answer(device)

    def _get_controller(self, device):
        if device and device.is_switchboard():
            if device.vendor == 'Aastra':
                return self._aastra_controller
            elif device.vendor == 'Snom':
                return self._snom_controller
            elif device.vendor == 'Yealink':
                return self._yealink_controller

        return self._base_controller

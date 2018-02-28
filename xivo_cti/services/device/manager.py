# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.services.device.controller.aastra import AastraController
from xivo_cti.services.device.controller.base import BaseController
from xivo_cti.services.device.controller.polycom import PolycomController
from xivo_cti.services.device.controller.snom import SnomController
from xivo_cti.services.device.controller.yealink import YealinkController


class DeviceManager(object):

    def __init__(self, ami_class, cti_provd_client):
        self._base_controller = BaseController(ami_class)
        self._aastra_controller = AastraController(ami_class)
        self._polycom_controller = PolycomController.new_from_config()
        self._snom_controller = SnomController.new_from_config()
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
            elif device.vendor == 'Polycom':
                return self._polycom_controller
            elif device.vendor == 'Snom':
                return self._snom_controller
            elif device.vendor == 'Yealink':
                return self._yealink_controller

        return self._base_controller

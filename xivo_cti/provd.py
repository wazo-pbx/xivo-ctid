# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_cti.model.device import Device
from wazo_provd_client import Client as ProvdClient
from wazo_provd_client.exceptions import ProvdError

logger = logging.getLogger(__name__)


class CTIProvdClient(object):

    def __init__(self, provd_client):
        self._dev_mgr = provd_client.devices

    def find_device(self, device_id):
        try:
            provd_device = self._dev_mgr.get(device_id)
        except ProvdError:
            pass
        except Exception as e:
            logger.error('Unexpected error while retrieving device: %s', e)
        else:
            return Device.new_from_provd_device(provd_device)

        return None

    @classmethod
    def new_from_config(cls, provd_config):
        return cls(ProvdClient(**provd_config))

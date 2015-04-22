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

import logging

from xivo_cti.model.device import Device
from xivo_provd_client import new_provisioning_client_from_config, NotFoundError

logger = logging.getLogger(__name__)


class CTIProvdClient(object):

    def __init__(self, provd_client):
        self._dev_mgr = provd_client.device_manager()

    def find_device(self, device_id):
        try:
            provd_device = self._dev_mgr.get(device_id)
        except NotFoundError:
            pass
        except Exception as e:
            logger.error('Unexpected error while retrieving device: %s', e)
        else:
            return Device.new_from_provd_device(provd_device)

        return None

    @classmethod
    def new_from_config(cls, provd_config):
        return cls(new_provisioning_client_from_config(provd_config))

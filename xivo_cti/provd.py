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
from xivo_provd_client import new_provisioning_client, NotFoundError

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
        host = provd_config.pop('host', 'localhost')
        port = provd_config.pop('port', 8666)
        username = provd_config.pop('username', None)
        password = provd_config.pop('password', None)
        https = provd_config.pop('https', False)
        if provd_config:
            logger.warning('Ignored provd config parameters: %s', provd_config.keys())

        scheme = 'https' if https else 'http'
        uri = '{}://{}:{}/provd'.format(scheme, host, port)
        if username and password:
            credentials = (username, password)
        else:
            credentials = None
        provd_client = new_provisioning_client(uri, credentials)
        return cls(provd_client)

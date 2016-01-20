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

import logging
import sys
import threading

import xivo_dao

from xivo.consul_helpers import NotifyingRegisterer, RegistererError

from xivo_cti import config
from xivo_cti import cti_config
from xivo_cti.ioc.context import context
from xivo_cti.ioc import register_class

logger = logging.getLogger(__name__)


class ServiceDiscovery(object):

    def __init__(self, service_name, config, publisher, check=None):
        self._check = check or self._default_check
        self._registerer = NotifyingRegisterer.from_config(service_name, publisher, config)

        self._retry_interval = config['service_discovery']['retry_interval']
        self._refresh_interval = config['service_discovery']['refresh_interval']

        self._thread = threading.Thread(target=self._loop)
        self._sleep_event = threading.Event()
        self._thread.daemon = True
        self._thread.name = 'ServiceDiscoveryThread'

        self._done = False
        self._registered = False

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, _, __, ___):
        if self._thread.is_alive():
            logger.debug('service_discovery: waiting for the service discovery thread to complete')
            self._done = True
            self._wake()
            self._thread.join()

        try:
            self._registerer.deregister()
        except Exception:
            logger.exception('service_discovery: failed to deregister')

    def _loop(self):
        while not self._done:
            service_ready = self._check()
            if service_ready:
                self._success()
            else:
                self._fail()

    def _sleep(self, interval):
        self._sleep_event.wait(interval)

    def _wake(self):
        self._sleep_event.set()

    def _success(self):
        if not self._registered:
            try:
                self._registerer.register()
                self._registered = True
            except RegistererError:
                logger.exception('service_discovery: failed to register service')
                logger.info('service_discovery: registration failed, retrying in %s seconds', self._retry_interval)
                return self._fail()

        # TTL here
        self._sleep(self._refresh_interval)

    def _fail(self):
        self._sleep(self._retry_interval)

    def _default_check(self):
        return True


def main():
    cti_config.init_cli_config(sys.argv[1:])
    cti_config.init_config_file()
    cti_config.init_auth_config()
    xivo_dao.init_db_from_config(config)
    cti_config.update_db_config()

    register_class.setup()

    ctid = context.get('cti_server')
    ctid.setup()
    publisher = context.get('bus_publisher')
    with ServiceDiscovery('xivo-ctid', config, publisher):
        ctid.run()


if __name__ == '__main__':
    main()

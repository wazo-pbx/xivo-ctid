# -*- coding: utf-8 -*-

# Copyright (C) 2007-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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

import sys
import logging

import xivo_dao

from functools import partial
from xivo.config_helper import get_xivo_uuid
from xivo.consul_helpers import ServiceCatalogRegistration
from xivo.user_rights import change_user
from xivo.xivo_logging import setup_logging, silence_loggers

from xivo_cti import config
from xivo_cti import cti_config
from xivo_cti.ioc.context import context
from xivo_cti.ioc import register_class
from xivo_cti.service_discovery import self_check

logger = logging.getLogger(__name__)


def main():
    cti_config.init_cli_config(sys.argv[1:])
    cti_config.init_config_file()
    cti_config.init_auth_config()
    xivo_dao.init_db_from_config(config)
    cti_config.update_db_config()

    user = config.get('user')
    if user:
        change_user(user)

    setup_logging(config['logfile'], config['foreground'], config['debug'])
    silence_loggers(['amqp', 'urllib3', 'Flask-Cors', 'kombu', 'stevedore.extension'], logging.WARNING)

    xivo_uuid = get_xivo_uuid(logger)

    register_class.setup(xivo_uuid)

    ctid = context.get('cti_server')
    ctid.setup()

    with ServiceCatalogRegistration('xivo-ctid',
                                    xivo_uuid,
                                    config['consul'],
                                    config['service_discovery'],
                                    config['bus'],
                                    partial(self_check, config)):
        ctid.run()


if __name__ == '__main__':
    main()

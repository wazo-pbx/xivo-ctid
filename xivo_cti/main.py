# -*- coding: utf-8 -*-
# Copyright (C) 2007-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

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

# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_cti.cti.cti_command import CTICommandClass

logger = logging.getLogger(__name__)


def _parse(msg, command):
    command.user_ids = [(xivo_uuid, user_id) for (xivo_uuid, user_id) in msg['user_ids']]


RegisterUserStatus = CTICommandClass('register_user_status_update', None, _parse)
RegisterUserStatus.add_to_registry()

# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_cti.cti.cti_command import CTICommandClass

logger = logging.getLogger(__name__)


def _parse(msg, command):
    command.endpoint_ids = [(xivo_uuid, endpoint_id) for (xivo_uuid, endpoint_id) in msg['endpoint_ids']]


RegisterEndpointStatus = CTICommandClass('register_endpoint_status_update', None, _parse)
RegisterEndpointStatus.add_to_registry()

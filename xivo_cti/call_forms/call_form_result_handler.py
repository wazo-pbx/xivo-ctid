# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging
import pprint
import re

from xivo_bus.resources.cti.event import CallFormResultEvent

logger = logging.getLogger(__name__)


class CallFormResultHandler(object):

    _variable_pattern = re.compile(r'XIVOFORM_([\w_]+)')

    def __init__(self, bus_publisher):
        self._bus_publisher = bus_publisher

    def parse(self, user_id, variables):
        self._send_call_form_result(
            user_id,
            self._clean_variables(variables),
        )

    def _send_call_form_result(self, user_id, variables):
        logger.debug('Call form result received for user %s with variables\n%s',
                     user_id, pprint.pformat(variables))
        event = CallFormResultEvent(user_id, variables)
        self._bus_publisher.publish(event)

    def _clean_variables(self, variables):
        return dict(
            (self._clean_key(key), value)
            for key, value in variables.iteritems()
            if self._is_valid_key(key)
        )

    def _is_valid_key(self, key):
        return self._variable_pattern.match(key) is not None

    def _clean_key(self, key):
        return self._variable_pattern.match(key).group(1)

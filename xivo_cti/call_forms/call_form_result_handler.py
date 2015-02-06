# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
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
import pprint
import re

from xivo_bus import Marshaler
from xivo_bus.resources.cti.event import CallFormResultEvent
from xivo_cti import config

logger = logging.getLogger(__name__)


class CallFormResultHandler(object):

    _marshaler = Marshaler()
    _variable_pattern = re.compile(r'XIVOFORM_([\w_]+)')

    def __init__(self, bus_publish):
        self._publish_bus_msg = bus_publish

    def parse(self, user_id, variables):
        self._send_call_form_result(
            user_id,
            self._clean_variables(variables),
        )

    def _send_call_form_result(self, user_id, variables):
        logger.debug('Call form result received for user %s with variables\n%s',
                     user_id, pprint.pformat(variables))
        msg = self._marshaler.marshal_message(CallFormResultEvent(user_id, variables))
        self._publish_bus_msg(msg, routing_key=config['bus']['routing_keys']['call_form_result'])

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

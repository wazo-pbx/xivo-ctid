# -*- coding: utf-8 -*-

import logging

from xivo_cti import dao

logger = logging.getLogger(__name__)


class CurrentCallFormatter(object):

    def __init__(self):
        self._state = {}

    def get_line_current_call(self, line_identity):
        calls = []

        for call in self._state.get(line_identity, {}):
            try:
                formatted_call = self._format_call(call)
            except LookupError:
                logger.warning('Could not retrieve channel information for the following call %s', call)
            else:
                calls.append(formatted_call)

        return {'class': 'current_calls',
                'current_calls': calls}

    def _format_call(self, call):
        caller_id = dao.channel.get_caller_id_name_number(call['channel'])
        return {'cid_name': caller_id[0],
                'cid_number': caller_id[1],
                'call_status': 'up',
                'call_start': call['bridge_time']}

# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
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
import re

from xivo_cti import config
from xivo_cti.ioc.context import context
from xivo_cti.interfaces import interfaces

logger = logging.getLogger('interface_webi')

_CMD_WEBI_PATTERN = re.compile(r'xivo\[(.+),(add|edit|delete|deleteall|enable|disable),(.*)\]')
_OBJECTS = [
    'user',
    'device',
    'line',
    'phone',
    'agent',
    'queue',
    'meetme',
    'voicemail',
]


class WEBI(interfaces.Interfaces):
    kind = 'WEBI'

    def __init__(self, ctiserver, queue_member_updater):
        interfaces.Interfaces.__init__(self, ctiserver)
        self._queue_member_updater = queue_member_updater

    def _object_request_cmd(self, sre_obj):
        object_name = sre_obj.group(1)
        state = sre_obj.group(2)
        id = sre_obj.group(3) if sre_obj.group(3) else None
        if object_name not in _OBJECTS:
            logger.warning('WEBI did an unknow object %s', object_name)
        else:
            msg_data = {
                'object_name': object_name,
                'state': state,
                'id': id
            }
            self._ctiserver.update_config_list.append(msg_data)
            if object_name == 'meetme':
                context.get('meetme_service_manager').initialize()

    def manage_connection(self, msg):
        response = [{'closemenow': True}]

        live_reload_conf = config['main']['live_reload_conf']

        if not live_reload_conf:
            logger.info('WEBI command received (%s) but live reload configuration has been disabled', msg)
            return response

        logger.info('WEBI command received: %s', msg)

        sre_obj = _CMD_WEBI_PATTERN.match(msg)

        if msg == 'xivo[cticonfig,update]':
            self._ctiserver.update_config_list.append(msg)
        elif msg == 'xivo[queuemember,update]':
            self._queue_member_updater.on_webi_update()
        elif sre_obj:
            self._object_request_cmd(sre_obj)
        else:
            logger.warning('WEBI did an unexpected request %s', msg)

        return response

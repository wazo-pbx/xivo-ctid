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
import random

from xivo_cti import ALPHANUMS
from xivo_cti import cti_fax, dao
from xivo_cti.ioc.context import context as cti_context
from xivo_cti.statistics.queue_statistics_encoder import QueueStatisticsEncoder

logger = logging.getLogger('cti_command')

REGCOMMANDS = [
    'getipbxlist',
    'keepalive',
    'faxsend',
    'getqueuesstats',
]


class Command(object):
    def __init__(self, connection, thiscommand):
        self._connection = connection
        self._ctiserver = self._connection._ctiserver
        self._commanddict = thiscommand
        self._queue_statistics_manager = cti_context.get('queue_statistics_manager')
        self._queue_statistics_encoder = QueueStatisticsEncoder()

    def parse(self):
        self.command = self._commanddict.get('class')
        self.commandid = self._commanddict.get('commandid')

        self.userid = self._connection.connection_details.get('userid')
        self.innerdata = self._ctiserver.safe

        messagebase = {'class': self.command}

        if self.commandid:
            messagebase['replyid'] = self.commandid

        if self.command in REGCOMMANDS:
            methodname = 'regcommand_%s' % self.command
            if hasattr(self, methodname):
                method_result = getattr(self, methodname)()
                if not method_result:
                    messagebase['warning_string'] = 'return_is_none'
                elif isinstance(method_result, str):
                    messagebase['error_string'] = method_result
                else:
                    messagebase.update(method_result)
            else:
                messagebase['warning_string'] = 'unimplemented'
        else:
            return []

        ackmessage = {'message': messagebase}
        if 'error_string' in messagebase:
            ackmessage['closemenow'] = True

        z = [ackmessage]
        return z

    def regcommand_getqueuesstats(self):
        if 'on' not in self._commanddict:
            return {}
        statistic_results = {}
        for queue_id, params in self._commanddict['on'].iteritems():
            queue_name = dao.queue.get_name_from_id(queue_id)
            statistic_results[queue_id] = self._queue_statistics_manager.get_statistics(queue_name,
                                                                                        int(params['xqos']),
                                                                                        int(params['window']))
        return self._queue_statistics_encoder.encode(statistic_results)

    def regcommand_faxsend(self):
        contexts = self.innerdata.xod_config['users'].get_contexts(self.userid)
        if not contexts:
            logger.info('faxsend: user %s tried to send a fax but has no context', self.userid)
            return

        context = contexts[0]
        fileid = ''.join(random.sample(ALPHANUMS, 10))
        size = self._commanddict['size']
        encoded_data = self._commanddict['data']
        destination = self._commanddict['destination']

        logger.info('faxsend: user %s is sending a %s bytes fax to %s@%s',
                    self.userid, size, destination, context)

        self.innerdata.faxes[fileid] = fax = cti_fax.Fax(self.innerdata, fileid, encoded_data)
        fax.setfaxparameters(self.userid, context, destination)
        fax.setrequester(self._connection)
        fax.launchasyncs()

    def regcommand_getipbxlist(self):
        return {'ipbxlist': ['xivo']}

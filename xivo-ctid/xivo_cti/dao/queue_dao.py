# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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
from xivo_cti.exception import NoSuchQueueException

logger = logging.getLogger(__name__)


class QueueDAO(object):

    def __init__(self, innerdata):
        self.innerdata = innerdata

    def _queue(self, queue_id):
        try:
            return self.innerdata.xod_config['queues'].keeplist[queue_id]
        except LookupError:
            raise NoSuchQueueException(queue_id)

    def get_number_context_from_name(self, queue_name):
        queues = self.innerdata.xod_config['queues'].keeplist
        for queue in queues.itervalues():
            if queue['name'] != queue_name:
                continue
            return queue['number'], queue['context']
        raise LookupError('No such queue %s' % queue_name)

    def get_name_from_id(self, queue_id):
        try:
            queue = self._queue(queue_id)
        except NoSuchQueueException:
            return None
        return queue['name']

    def get_id_from_name(self, queue_name):
        queue_list = self.innerdata.xod_config['queues'].keeplist
        for (queue_id, queue) in queue_list.iteritems():
            if queue['name'] == queue_name:
                return int(queue_id)
        return None

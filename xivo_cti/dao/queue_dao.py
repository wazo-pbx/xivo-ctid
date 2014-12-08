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


class QueueDAO(object):

    def __init__(self, innerdata):
        self.innerdata = innerdata

    def get_queue_from_name(self, queue_name):
        queues_list = self.innerdata.xod_config['queues']
        return queues_list.get_queue_by_name(queue_name)

    def get_id_from_name(self, queue_name):
        queue = self.get_queue_from_name(queue_name)
        if queue:
            return queue['id']
        return None

    def get_number_context_from_name(self, queue_name):
        queue = self.get_queue_from_name(queue_name)
        if queue:
            return queue['number'], queue['context']
        raise LookupError('No such queue %s' % queue_name)

    def get_queue_from_id(self, queue_id):
        queues_list = self.innerdata.xod_config['queues']
        return queues_list.keeplist.get(str(queue_id))

    def get_name_from_id(self, queue_id):
        queue = self.get_queue_from_id(queue_id)
        if queue:
            return queue['name']
        return None

    def get_ids(self):
        queues_list = self.innerdata.xod_config['queues']
        return queues_list.get_queues()

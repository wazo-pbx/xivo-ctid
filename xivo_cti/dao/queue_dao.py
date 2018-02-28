# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+


class QueueDAO(object):

    def __init__(self, innerdata):
        self.innerdata = innerdata

    def exists(self, queue_name):
        queues_list = self.innerdata.xod_config['queues']
        return queue_name in queues_list.queues_by_name

    def get_queue_from_name(self, queue_name):
        queues_list = self.innerdata.xod_config['queues']
        return queues_list.queues_by_name.get(queue_name)

    def get_id_from_name(self, queue_name):
        queue = self.get_queue_from_name(queue_name)
        if queue:
            return queue['id']
        return None

    def get_id_as_str_from_name(self, queue_name):
        queue = self.get_queue_from_name(queue_name)
        if queue:
            return str(queue['id'])
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
        return queues_list.keeplist.keys()

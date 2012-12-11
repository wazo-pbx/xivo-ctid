# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the souce tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import time

from xivo_cti.services.queue_service_manager import NotAQueueException

logger = logging.getLogger("InnerdataDAO")


class InnerdataDAO(object):

    def __init__(self, innerdata):
        self.innerdata = innerdata

    def get_queuemembers_config(self):
        return self.innerdata.queuemembers_config

    def get_queuemembers_static(self):
        queuemembers_config = self.innerdata.queuemembers_config
        ret = {}
        for queuemember in queuemembers_config:
            if queuemembers_config[queuemember]['membership'] == 'static':
                ret[queuemember] = queuemembers_config[queuemember]
        return ret

    def apply_queuemember_delta(self, delta):
        if delta.add:
            self.innerdata.queuemembers_config.update(delta.add)
        if delta.change:
            for changed_queuemember in delta.change:
                if changed_queuemember in self.innerdata.queuemembers_config:
                    self.innerdata.queuemembers_config[changed_queuemember].update(delta.change[changed_queuemember])
        if delta.delete:
            for deleted_key in delta.delete:
                self.innerdata.queuemembers_config.pop(deleted_key)

    def get_queuemember(self, queuemember_id):
        return self.innerdata.queuemembers_config[queuemember_id]

    def get_queue_id(self, queue_name):
        queue_id = self.innerdata.xod_config['queues'].idbyqueuename(queue_name)
        if queue_id is None:
            raise NotAQueueException()
        return queue_id

    def get_queue_ids(self):
        return self.innerdata.xod_config['queues'].get_queues()

    def get_presences(self, profile):
        profile_id = self.innerdata._config.getconfig('profiles').get(profile).get('userstatus')
        return self.innerdata._config.getconfig('userstatus').get(profile_id).keys()

    def set_agent_availability(self, agent_id, availability):
        agent_status = self.innerdata.xod_status['agents'][str(agent_id)]
        if availability != agent_status['availability']:
            agent_status['availability_since'] = time.time()
            agent_status['availability'] = availability

    def agent_status(self, agent_id):
        agent_status = self.innerdata.xod_status['agents'][str(agent_id)]
        return agent_status

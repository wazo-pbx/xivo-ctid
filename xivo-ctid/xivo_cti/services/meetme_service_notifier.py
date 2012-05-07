#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2011  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from copy import deepcopy

logger = logging.getLogger('meetme_service_notifier')


class MeetmeServiceNotifier(object):
    STATUS_MESSAGE = {'class': 'getlist',
                      'listname': 'meetmes',
                      'function': '',
                      'tipbxid': ''}

    def _prepare_message(self):
        msg = deepcopy(self.STATUS_MESSAGE)
        msg.update({'tipbxid': self.ipbx_id})
        return msg

    def _prepare_event_add(self, list):
        filter_status_msg = self._prepare_message()
        status_update = {'function': 'addconfig',
                         'list': [list]}
        filter_status_msg.update(status_update)
        return filter_status_msg

    def add(self, meetme_id):
        self.events_cti.put(self._prepare_event_add(meetme_id))

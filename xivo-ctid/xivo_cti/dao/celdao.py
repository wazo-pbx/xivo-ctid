# -*- coding: UTF-8 -*-

# XiVO CTI Server
# Copyright (C) 2009-2012  Avencall
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
from xivo_cti.dao.alchemy import dbconnection
from xivo_cti.dao.alchemy.cel import CEL
from xivo_cti.dao.helpers.cel_channel import CELChannel
from xivo_cti.dao.helpers.cel_exception import CELException


logger = logging.getLogger(__name__)


class CELDAO(object):
    def __init__(self, session):
        self._session = session

    def caller_id_by_unique_id(self, unique_id):
        cel_events = (self._session.query(CEL.cid_name, CEL.cid_num)
                      .filter(CEL.eventtype == 'CHAN_START')
                      .filter(CEL.uniqueid == unique_id)
                      .all())
        if not cel_events:
            raise CELException('no such CEL event with uniqueid %s' % unique_id)
        else:
            cid_name, cid_num = cel_events[0]
            return '"%s" <%s>' % (cid_name, cid_num)

    def channel_by_unique_id(self, unique_id):
        cel_events = (self._session.query(CEL)
                      .filter(CEL.uniqueid == unique_id)
                      .all())
        if not cel_events:
            raise CELException('no such CEL event with uniqueid %s' % unique_id)
        else:
            return CELChannel(cel_events)

    def cels_by_linked_id(self, linked_id):
        cel_events = (self._session.query(CEL)
                      .filter(CEL.linkedid == linked_id)
                      .all())
        if not cel_events:
            raise CELException('no such CEL event with linkedid %s' % linked_id)
        else:
            return cel_events

    def _channel_pattern_from_endpoint(self, endpoint):
        return "%s-%%" % endpoint

    def answered_channels_for_endpoint(self, endpoint, limit):
        channel_pattern = self._channel_pattern_from_endpoint(endpoint)
        query = (self._session.query(CEL.uniqueid)
                 .filter(CEL.channame.like(channel_pattern))
                 .filter(CEL.eventtype == 'CHAN_START')
                 .filter(CEL.uniqueid != CEL.linkedid)
                 .order_by(CEL.eventtime.desc()))
        channels = []
        for unique_id, in query:
            try:
                channel = self.channel_by_unique_id(unique_id)
            except CELException, e:
                # this can happen in the case the channel is alive
                logger.info('could not create CEL channel %s: %s', unique_id, e)
            else:
                if channel.is_answered():
                    channels.append(channel)
                    if len(channels) >= limit:
                        break
        return channels

    def missed_channels_for_endpoint(self, endpoint, limit):
        channel_pattern = self._channel_pattern_from_endpoint(endpoint)
        query = (self._session.query(CEL.uniqueid)
                 .filter(CEL.channame.like(channel_pattern))
                 .filter(CEL.eventtype == 'CHAN_START')
                 .filter(CEL.uniqueid != CEL.linkedid)
                 .order_by(CEL.eventtime.desc()))
        channels = []
        for unique_id, in query:
            try:
                channel = self.channel_by_unique_id(unique_id)
            except CELException, e:
                # this can happen in the case the channel is alive
                logger.info('could not create CEL channel %s: %s', unique_id, e)
            else:
                if not channel.is_answered():
                    channels.append(channel)
                    if len(channels) >= limit:
                        break
        return channels

    def outgoing_channels_for_endpoint(self, endpoint, limit):
        channel_pattern = self._channel_pattern_from_endpoint(endpoint)
        query = (self._session.query(CEL.uniqueid)
                 .filter(CEL.channame.like(channel_pattern))
                 .filter(CEL.eventtype == 'CHAN_START')
                 .filter(CEL.uniqueid == CEL.linkedid)
                 .order_by(CEL.eventtime.desc())
                 .limit(limit))
        channels = []
        for unique_id, in query:
            try:
                channel = self.channel_by_unique_id(unique_id)
            except CELException, e:
                # this can happen in the case the channel is alive
                logger.info('could not create CEL channel %s: %s', unique_id, e)
            else:
                channels.append(channel)
                if len(channels) >= limit:
                    break
        return channels

    @classmethod
    def new_from_uri(cls, uri):
        connection = dbconnection.get_connection(uri)
        return cls(connection.get_session())

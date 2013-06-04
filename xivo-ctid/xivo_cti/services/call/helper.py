# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

import collections
import re

from xivo_cti.model.endpoint_status import EndpointStatus
from xivo_dao import line_dao
channel_regexp = re.compile(r'(sip|sccp)/(\w+).*', re.I)

ProtocolInterface = collections.namedtuple('ProtocolInterface', ['protocol', 'interface'])


class ChannelState(object):
    ring = '4'
    ringing = '5'


class InvalidChannel(ValueError):
    def __init__(self, invalid_channel):
        ValueError.__init__(self, 'the channel %s is invalid' % invalid_channel)


def protocol_interface_from_channel(channel):
    matches = channel_regexp.match(channel)
    if matches is None:
        raise InvalidChannel(channel)
    protocol = matches.group(1)
    interface = matches.group(2)

    return ProtocolInterface(protocol, interface)


def channel_state_to_status(channel_state):
    if channel_state == ChannelState.ring:
        return EndpointStatus.ringback_tone
    elif channel_state == ChannelState.ringing:
        return EndpointStatus.ringing
    else:
        return None


def get_extension_from_channel(channel):
    protocol_interface = protocol_interface_from_channel(channel)
    extension = line_dao.get_extension_from_protocol_interface(protocol_interface.protocol,
                                                               protocol_interface.interface)
    return extension

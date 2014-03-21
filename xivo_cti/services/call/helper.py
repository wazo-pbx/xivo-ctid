# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from xivo.asterisk.extension import Extension
from xivo.asterisk.protocol_interface import protocol_interface_from_channel
from xivo_cti.model.endpoint_status import EndpointStatus
from xivo_dao import line_dao


class ChannelState(object):
    ring = '4'
    ringing = '5'
    talking = '6'


def channel_state_to_status(channel_state):
    if channel_state == ChannelState.ring:
        return EndpointStatus.ringback_tone
    elif channel_state == ChannelState.ringing:
        return EndpointStatus.ringing
    elif channel_state == ChannelState.talking:
        return EndpointStatus.talking
    else:
        return None


def get_extension_from_channel(channel):
    protocol_interface = protocol_interface_from_channel(channel)

    try:
        extension = line_dao.get_extension_from_protocol_interface(protocol_interface.protocol,
                                                                   protocol_interface.interface)
    except (LookupError, ValueError):
        extension = Extension(number='', context='', is_internal=False)
    return extension

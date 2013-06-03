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

from xivo_cti.model.line_status import LineStatus


class ChannelState(object):
    ring = '4'
    ringing = '5'


def interface_from_channel(channel):
    return channel.split('-', 1)[0]


def channel_state_to_status(channel_state):
    if channel_state == ChannelState.ring:
        return LineStatus.ringback_tone
    elif channel_state == ChannelState.ringing:
        return LineStatus.ringing

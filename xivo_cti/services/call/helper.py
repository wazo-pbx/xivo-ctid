# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo.asterisk.extension import Extension
from xivo.asterisk.protocol_interface import protocol_interface_from_channel
from xivo_cti.model.endpoint_status import EndpointStatus

from xivo_dao.helpers.db_utils import session_scope
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
        with session_scope():
            extension = line_dao.get_extension_from_protocol_interface(protocol_interface.protocol,
                                                                       protocol_interface.interface)
    except (LookupError, ValueError):
        extension = Extension(number='', context='', is_internal=False)
    return extension

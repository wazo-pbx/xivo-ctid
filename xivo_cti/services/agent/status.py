# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+


class AgentStatus(object):
    available = 'available'
    on_call_nonacd_incoming_internal = 'on_call_nonacd_incoming_internal'
    on_call_nonacd_incoming_external = 'on_call_nonacd_incoming_external'
    on_call_nonacd_outgoing_internal = 'on_call_nonacd_outgoing_internal'
    on_call_nonacd_outgoing_external = 'on_call_nonacd_outgoing_external'
    unavailable = 'unavailable'
    logged_out = 'logged_out'

# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _parse(msg, command):
    command.queue_name = msg['queue_name']


HoldSwitchboard = CTICommandClass('hold_switchboard', None, _parse)
HoldSwitchboard.add_to_registry()

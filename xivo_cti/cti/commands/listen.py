# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _match(msg):
    return msg['command'] == 'listen'


def _parse(msg, command):
    command.destination = msg['destination']


Listen = CTICommandClass('ipbxcommand', _match, _parse)
Listen.add_to_registry()

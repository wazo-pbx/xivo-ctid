# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _parse(msg, command):
    command.number = msg['number']


AttendedTransfer = CTICommandClass('attended_transfer', None, _parse)
AttendedTransfer.add_to_registry()

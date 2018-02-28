# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _parse(msg, command):
    command.number = msg['number']


DirectTransfer = CTICommandClass('direct_transfer', None, _parse)
DirectTransfer.add_to_registry()

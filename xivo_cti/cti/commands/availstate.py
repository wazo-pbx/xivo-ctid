# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _parse(msg, command):
    command.availstate = msg['availstate']


Availstate = CTICommandClass('availstate', None, _parse)
Availstate.add_to_registry()

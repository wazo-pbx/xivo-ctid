# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _parse(msg, command):
    command.size = int(msg['size'])


History = CTICommandClass('history', None, _parse)
History.add_to_registry()

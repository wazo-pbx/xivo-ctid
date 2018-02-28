# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _parse(msg, command):
    command.unique_id = msg['unique_id']

Answer = CTICommandClass('answer', None, _parse)
Answer.add_to_registry()

# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _parse(msg, command):
    command.unique_id = msg['unique_id']


ResumeSwitchboard = CTICommandClass('resume_switchboard', None, _parse)
ResumeSwitchboard.add_to_registry()

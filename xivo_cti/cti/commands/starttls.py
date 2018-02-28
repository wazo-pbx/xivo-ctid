# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _parse(msg, command):
    command.status = msg.get('status')


StartTLS = CTICommandClass('starttls', None, _parse)
StartTLS.add_to_registry()

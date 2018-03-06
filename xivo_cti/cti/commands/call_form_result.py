# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _parse(msg, command):
    command.variables = msg.get('infos', {}).get('variables', {})


CallFormResult = CTICommandClass('call_form_result', None, _parse)
CallFormResult.add_to_registry()

# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _new_class(function_name, value):

    def match(msg):
        return msg['function'] == function_name and msg['value'] == value

    def parse(msg, command):
        command.target = msg.get('target')

    return CTICommandClass('featuresput', match, parse)


EnableDND = _new_class('enablednd', True)
EnableDND.add_to_registry()

DisableDND = _new_class('enablednd', False)
DisableDND.add_to_registry()

EnableFilter = _new_class('incallfilter', True)
EnableFilter.add_to_registry()

DisableFilter = _new_class('incallfilter', False)
DisableFilter.add_to_registry()

EnableRecording = _new_class('enablerecording', True)
EnableRecording.add_to_registry()

DisableRecording = _new_class('enablerecording', False)
DisableRecording.add_to_registry()

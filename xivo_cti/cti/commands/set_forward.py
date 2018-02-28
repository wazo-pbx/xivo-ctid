# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _new_class(enable_name, enable_value, destination_name):

    def match(msg):
        return (
            msg['function'] == 'fwd' and
            enable_name in msg['value'] and
            msg['value'][enable_name] == enable_value
        )

    def parse(msg, command):
        command.destination = msg['value'][destination_name]

    return CTICommandClass('featuresput', match, parse)


EnableBusyForward = _new_class('enablebusy', True, 'destbusy')
EnableBusyForward.add_to_registry()

DisableBusyForward = _new_class('enablebusy', False, 'destbusy')
DisableBusyForward.add_to_registry()

EnableNoAnswerForward = _new_class('enablerna', True, 'destrna')
EnableNoAnswerForward.add_to_registry()

DisableNoAnswerForward = _new_class('enablerna', False, 'destrna')
DisableNoAnswerForward.add_to_registry()

EnableUnconditionalForward = _new_class('enableunc', True, 'destunc')
EnableUnconditionalForward.add_to_registry()

DisableUnconditionalForward = _new_class('enableunc', False, 'destunc')
DisableUnconditionalForward.add_to_registry()

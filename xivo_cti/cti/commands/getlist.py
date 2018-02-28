# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _parse(msg, command):
    command.list_name = msg['listname']
    command.item_id = msg.get('tid')


def _new_class(function_name):
    def match(msg):
        return msg['function'] == function_name

    return CTICommandClass('getlist', match, _parse)


ListID = _new_class('listid')
ListID.add_to_getlist_registry('listid')

UpdateConfig = _new_class('updateconfig')
UpdateConfig.add_to_getlist_registry('updateconfig')

UpdateStatus = _new_class('updatestatus')
UpdateStatus.add_to_getlist_registry('updatestatus')

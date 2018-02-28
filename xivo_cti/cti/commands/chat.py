# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import uuid

from xivo_cti.cti.cti_command import CTICommandClass


def _check_valid_uuid(value):
    uuid.UUID(value)
    return value


def _parse(msg, command):
    command.alias = msg['alias']
    command.remote_xivo_uuid = _check_valid_uuid(msg['to'][0])
    command.remote_user_uuid = _check_valid_uuid(msg['to'][1])
    command.text = msg['text']

Chat = CTICommandClass('chitchat', None, _parse)
Chat.add_to_registry()

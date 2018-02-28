# -*- coding: utf-8 -*-
# Copyright 2007-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _parse_login_capas(msg, command):
    command.capaid = int(msg['capaid'])
    command.state = msg['state']


LoginCapas = CTICommandClass('login_capas', None, _parse_login_capas)
LoginCapas.add_to_registry()


def _parse_login_id(msg, command):
    command.company = msg['company']
    command.ident = msg['ident']
    command.userlogin = msg['userlogin']
    # In wazo 17.16 the field was changed from xivoversion to wazoversion
    command.xivo_version = msg.get('wazoversion') or msg.get('xivoversion')


LoginID = CTICommandClass('login_id', None, _parse_login_id)
LoginID.add_to_registry()


def _parse_login_pass(msg, command):
    command.password = msg['password']


LoginPass = CTICommandClass('login_pass', None, _parse_login_pass)
LoginPass.add_to_registry()

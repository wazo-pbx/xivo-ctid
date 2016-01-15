# -*- coding: utf-8 -*-

# Copyright (C) 2007-2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_cti.cti.cti_command import CTICommandClass


def _parse_login_capas(msg, command):
    command.capaid = msg['capaid']
    command.state = msg['state']

LoginCapas = CTICommandClass('login_capas', None, _parse_login_capas)
LoginCapas.add_to_registry()


def _parse_login_id(msg, command):
    command.company = msg['company']
    command.ident = msg['ident']
    command.userlogin = msg['userlogin']
    command.xivo_version = msg['xivoversion']


LoginID = CTICommandClass('login_id', None, _parse_login_id)
LoginID.add_to_registry()


def _parse_login_pass(msg, command):
    command.password = msg['password']


LoginPass = CTICommandClass('login_pass', None, _parse_login_pass)
LoginPass.add_to_registry()

# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xivo_cti.cti.cti_command import CTICommand
from xivo_cti.cti.cti_command_factory import CTICommandFactory
from xivo_cti.cti.commands.set_user_service import SetUserService
from xivo_cti.cti.commands.user_service.set_forward import SetForward


class EnableBusyForward(SetForward):

    FUNCTION_NAME = 'fwd'
    ENABLE_NAME = 'enablebusy'
    DESTINATION_NAME = 'destbusy'

    required_fields = [CTICommand.CLASS, SetUserService.FUNCTION, SetUserService.VALUE]
    conditions = [(CTICommand.CLASS, SetUserService.COMMAND_CLASS),
                  (SetUserService.FUNCTION, FUNCTION_NAME),
                  ((SetUserService.VALUE, ENABLE_NAME), True)]
    _callbacks_with_params = []

CTICommandFactory.register_class(EnableBusyForward)

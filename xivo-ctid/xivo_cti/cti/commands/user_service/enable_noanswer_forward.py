# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

from xivo_cti.cti import cti_command_registry
from xivo_cti.cti.commands.user_service.set_forward import SetForward


class EnableNoAnswerForward(SetForward):

    enable_name = 'enablerna'
    enable_value = True
    destination_name = 'destrna'


EnableNoAnswerForward = EnableNoAnswerForward()
cti_command_registry.register_class(EnableNoAnswerForward)

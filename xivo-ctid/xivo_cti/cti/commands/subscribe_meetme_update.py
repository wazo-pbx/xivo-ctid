# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

from xivo_cti.cti.commands.subscribe import Subscribe
from xivo_cti.cti.cti_command import CTICommand
from xivo_cti.cti.cti_command_factory import CTICommandFactory


class SubscribeMeetmeUpdate(Subscribe):

    MESSAGE_NAME = 'meetme_update'

    conditions = [(CTICommand.CLASS, Subscribe.COMMAND_CLASS),
                  (Subscribe.MESSAGE, MESSAGE_NAME)]
    _callbacks_with_params = []


CTICommandFactory.register_class(SubscribeMeetmeUpdate)

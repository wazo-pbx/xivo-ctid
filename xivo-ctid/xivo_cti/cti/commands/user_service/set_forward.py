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

from xivo_cti.cti.cti_command import AbstractCTICommandClass


class SetForward(AbstractCTICommandClass):

    class_name = 'featuresput'

    def _match(self, msg):
        return (
            msg['function'] == 'fwd' and
            self.enable_name in msg['value'] and
            msg['value'][self.enable_name] == self.enable_value
        )

    def _parse(self, msg, command):
        command.destination = msg['value'][self.destination_name]

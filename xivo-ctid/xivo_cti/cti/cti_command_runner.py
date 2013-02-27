# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

import logging
from xivo_cti.cti.cti_reply_generator import CTIReplyGenerator

logger = logging.getLogger('CTICommandRunner')


class CTICommandRunner(object):

    def __init__(self):
        self._reply_generator = CTIReplyGenerator()

    def _get_arguments(self, command, args):
        return [getattr(command, arg) for arg in args]

    def run(self, command):
        for callback in command.callbacks_with_params():
            function, args = callback
            arg_list = self._get_arguments(command, args)
            reply = function(*arg_list)
            if reply:
                return self._reply_generator.get_reply(reply[0], command, reply[1], reply[2] if len(reply) >= 3 else False)
        return {'status': 'OK'}

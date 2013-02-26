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

import collections


class CTICommandFactory(object):

    _registered_classes = set()
    _classes_by_msg_class = collections.defaultdict(list)

    def get_command(self, msg):
        msg_class = msg['class']
        classes = self._classes_by_msg_class.get(msg_class,[])
        matching_classes = [klass for klass in classes if klass.match_message(msg)]
        return matching_classes

    @classmethod
    def register_class(cls, klass_to_register):
        msg_class = klass_to_register.COMMAND_CLASS
        cls._registered_classes.add(klass_to_register)
        cls._classes_by_msg_class[msg_class].append(klass_to_register)

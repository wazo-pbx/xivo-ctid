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

logger = logging.getLogger(__name__)


class Destination(object):

    def __init__(self, url_type, ipbx, value):
        self.dest_type = url_type
        self.ipbxid = ipbx
        self.value = value

    def __eq__(self, other):
        return (self.dest_type == other.dest_type
                and self.ipbxid == other.ipbxid
                and self.value == other.value)

    def to_exten(self):
        logger.warning('Unimplemented to exten method for type %s', self.dest_type)

# -*- coding: utf-8 -*-

# XiVO CTI Server
# Copyright (C) 2009-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

logger = logging.getLogger("InnerdataDAO")

class InnerdataDAO(object):

    def get_queuemembers_config(self):
        return self.innerdata.queuemembers_config

    def apply_queuemember_delta(self, delta):
        if delta.add:
            self.innerdata.queuemembers_config.update(delta.add)
        if delta.change:
            self.innerdata.queuemembers_config.update(delta.change)
        if delta.delete:
            for deleted_key in delta.delete:
                self.innerdata.queuemembers_config.pop(deleted_key)

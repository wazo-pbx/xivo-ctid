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
# contracted with Avencall. See the LICENSE file at top of the souce tree
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

from xivo_cti.ami.ami_logger import AMILogger

log_ami_events_statusrequest = True


class AMIStatusRequestLogger(AMILogger):
    _instance = None
    _log_header = 'AMI status request logger'
    logged_events = ['Agents',
                     'CoreShowChannel',
                     'ParkedCallStatus',
                     'RegistryEntry',
                     'Status',
                     ]

    def log_ami_event(self, event):
        if log_ami_events_statusrequest:
            super(AMIStatusRequestLogger, self).log_ami_event(event)

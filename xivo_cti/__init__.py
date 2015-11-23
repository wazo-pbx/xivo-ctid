# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

import ssl
import string

from UserDict import UserDict

__all__ = []

CTI_PROTOCOL_VERSION = '1.2'
DAEMONNAME = 'xivo-ctid'
SSLPROTO = ssl.PROTOCOL_TLSv1
ALPHANUMS = string.uppercase + string.lowercase + string.digits

config = UserDict()

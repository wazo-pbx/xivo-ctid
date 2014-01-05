# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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

import re
import logging
from xivo import caller_id

logger = logging.getLogger('extension')

VALID_EXTENSION_PATTERN = re.compile('[^a-z0-9#*+]', re.I)


def normalize_exten(exten):
    try:
        extentodial = caller_id.extract_number(exten)
    except ValueError:
        extentodial = re.sub(VALID_EXTENSION_PATTERN, '', exten)

    if not extentodial:
        raise ValueError('Invalid extension %s', exten)

    return extentodial

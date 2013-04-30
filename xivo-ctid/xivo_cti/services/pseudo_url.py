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

import re

from xivo_cti.services.destination import Destination


class PseudoURL(object):

    'voicemail:xivo/123'
    url_pattern = re.compile(r'(\w+):(\w+)/(\d+)')

    @classmethod
    def parse(cls, url):
        result = cls.url_pattern.match(url)
        if not result:
            raise ValueError('Input does not match the URL pattern %s', url)
        return Destination(result.group(1), result.group(2), result.group(3))

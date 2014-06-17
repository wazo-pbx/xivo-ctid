# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

import json
import logging
import requests

logger = logging.getLogger()


class Dird:

    def __init__(self):
        pass  # ioc context needs default constructor

    def headers(self, profile, callback, user_id):
        url = 'http://localhost:50060/0.1/directories/lookup/{profile}/headers'.format(profile=profile)
        result = requests.get(url)
        result = json.loads(result)
        logger.debug('calling %s with %s', callback, (user_id, result))
        callback(user_id, result)

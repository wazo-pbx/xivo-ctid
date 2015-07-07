# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

from xivo_cti.services.bridge.bridge import Bridge

logger = logging.getLogger(__name__)


class BridgeManager(object):

    def __init__(self):
        self._bridges = {}

    # package private method
    def _add_bridge(self, bridge_id, bridge_type):
        self._bridges[bridge_id] = Bridge(bridge_id, bridge_type)

    # package private method
    def _remove_bridge(self, bridge_id):
        try:
            del self._bridges[bridge_id]
        except KeyError:
            logger.warning('Failed to remove bridge %s: no such bridge', bridge_id)

    def get_bridge(self, bridge_id):
        return self._bridges.get(bridge_id)

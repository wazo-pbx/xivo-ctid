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

from xivo_cti.cti_anylist import ContextAwareAnyList

import logging

logger = logging.getLogger('meetmelist')


class MeetmeList(ContextAwareAnyList):

    def __init__(self, newurls=[], useless=None):
        self.anylist_properties = {'name': 'meetme',
                                   'urloptions': (1, 5, True)}
        ContextAwareAnyList.__init__(self, newurls)

    def update(self):
        ret = ContextAwareAnyList.update(self)
        self.reverse_index = {}
        for idx, ag in self.keeplist.iteritems():
            if ag['confno'] not in self.reverse_index:
                self.reverse_index[ag['confno']] = idx
            else:
                logger.warning('2 meetme have the same room number')
        return ret

    def update_computed_fields(self, newlist):
        for item in newlist.itervalues():
            item['pin_needed'] = bool(item.get('pin'))

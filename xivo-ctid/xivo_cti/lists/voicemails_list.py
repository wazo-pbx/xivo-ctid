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

import logging
from xivo_cti.cti_anylist import ContextAwareAnyList

logger = logging.getLogger('voicemaillist')


class VoicemailsList(ContextAwareAnyList):

    def __init__(self, innerdata):
        self._innerdata = innerdata
        ContextAwareAnyList.__init__(self, 'voicemails')

    def init_data(self):
        ContextAwareAnyList.init_data(self)
        self.reverse_index = {}
        for idx, ag in self.keeplist.iteritems():
            rev = '%s@%s' % (ag['mailbox'], ag['context'])
            if rev not in self.reverse_index:
                self.reverse_index[rev] = idx
            else:
                logger.warning('2 voicemails have the same mailbox@context')

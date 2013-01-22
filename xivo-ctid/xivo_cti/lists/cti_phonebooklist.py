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

import logging
from xivo_cti.cti_anylist import AnyList

logger = logging.getLogger('phonebook')


class PhonebookList(AnyList):

    def __init__(self, newurls=[], useless=None):
        self.anylist_properties = {'name': 'phonebook',
                                   'urloptions': (1, 5, True)}
        AnyList.__init__(self, newurls)
        self.commandclass = self
        self.getter = '_getphonebook'

    def setcommandclass(self, commandclass):
        pass

    def setgetter(self, getter):
        pass

    def _getphonebook(self, jsonreply):
        pblist = {}
        for pitem in jsonreply:
            pbitem = {}
            for i1, v1 in pitem.iteritems():
                if isinstance(v1, dict):
                    for i2, v2 in v1.iteritems():
                        if isinstance(v2, dict):
                            for i3, v3 in v2.iteritems():
                                idx = '.'.join([i1, i2, i3])
                                pbitem[idx] = v3
                        else:
                            idx = '.'.join([i1, i2])
                            pbitem[idx] = v2
                else:
                    pbitem[i1] = v1
            myid = pbitem.get('phonebook.id')
            pblist[myid] = pbitem
        return pblist

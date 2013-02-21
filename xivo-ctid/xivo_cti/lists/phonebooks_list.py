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


class PhonebooksList(AnyList):

    def __init__(self, innerdata):
        self._innerdata = innerdata
        AnyList.__init__(self, 'phonebooks')

    def init_data(self):
        AnyList.init_data(self)
        self.keeplist = self._getphonebook(self.keeplist)

    def add(self, id):
        raw_data = self.listname_obj.get(id)
        self.keeplist.update(self._prepare_phonebook_data(id, raw_data[id]))
        AnyList.add_notifier(self, id)

    def edit(self, id):
        raw_data = self.listname_obj.get(id)
        self.keeplist.update(self._prepare_phonebook_data(id, raw_data[id]))
        AnyList.edit_notifier(self, id)

    def _getphonebook(self, raw_data_dict):
        res = {}
        for phonebook_id, phonebook_dict in raw_data_dict.iteritems():
            res.update(self._prepare_phonebook_data(phonebook_id, phonebook_dict))
        return res

    def _prepare_phonebook_data(self, phonebook_id, phonebook_dict):
        tmp = {}
        for i1, v1 in phonebook_dict.iteritems():
            if isinstance(v1, dict):
                for i2, v2 in v1.iteritems():
                    if isinstance(v2, dict):
                        for i3, v3 in v2.iteritems():
                            idx = '.'.join([i1, i2, i3])
                            tmp[idx] = v3
                    else:
                        idx = '.'.join([i1, i2])
                        tmp[idx] = v2
            else:
                tmp[i1] = v1
        return {phonebook_id: tmp}

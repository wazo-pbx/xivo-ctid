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
# contracted with Avencall. See the LICENSE file at top of the source tree
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
import cti_urllist
from collections import defaultdict
from xivo_cti.context import context as cti_context
from xivo_cti.cti_config import Config

logger = logging.getLogger('anylist')


class AnyList(object):
    def __init__(self, newurls):
        self.commandclass = None
        self._ctiserver = None
        self.requested_list = {}
        self.keeplist = {}
        self.__clean_urls__()
        self.__add_urls__(newurls)

    def update(self):
        lstadd = []
        lstdel = []
        lstchange = {}
        oldlist = self.keeplist
        newlist = {}

        # Get new list from Web services.
        for urllist in self.requested_list.itervalues():
            gl = urllist.getlist(* self.anylist_properties['urloptions'])
            if gl == 2:
                tmplist = getattr(self.commandclass, self.getter)(urllist.jsonreply)
                newlist.update(tmplist)

        # Update computed fields, if any.
        self.update_computed_fields(newlist)

        # Compare old (self.keeplist) and new (newlist) list:
        # Compute the differences and update the current list.
        for a, b in newlist.iteritems():
            if a not in oldlist:
                self.keeplist[a] = b
                lstadd.append(a)
            else:
                oldfull = self.keeplist[a]
                if b != oldfull:
                    keywords = []
                    for bk, bv in b.iteritems():
                        oldval = self.keeplist[a][bk]
                        if bv != oldval:
                            self.keeplist[a][bk] = bv
                            keywords.append(bk)
                    if keywords:
                        lstchange[a] = keywords
        for a, b in oldlist.iteritems():
            if a not in newlist:
                lstdel.append(a)

        # Remove old items.
        for a in lstdel:
            del self.keeplist[a]

        return {'add': lstadd,
                'del': lstdel,
                'change': lstchange}

    def update_computed_fields(self, newlist):
        # "Virtual" function
        # You should reimplement it if the list items contains fields
        # that depends on other fields. See MeetmeList for an example.
        pass

    def setcommandclass(self, commandclass):
        self.commandclass = commandclass
        self._ctiserver = self.commandclass._ctiserver

    def setgetter(self, getter):
        self.getter = getter

    def __clean_urls__(self):
        self.requested_list = {}

    def __add_urls__(self, newurls):
        for url in newurls:
            if url not in self.requested_list:
                self.requested_list[url] = cti_urllist.UrlList(url)

    def setandupdate(self, newurls):
        self.__add_urls__(newurls)
        if not self.requested_list:
            return
        self.update()

    def list_ids_in_contexts(self, contexts):
        return self.keeplist.keys()

    def get_item_in_contexts(self, item_id, contexts):
        return self.keeplist.get(item_id)


class ContextAwareAnyList(AnyList):
    def __init__(self, newurls):
        AnyList.__init__(self, newurls)
        self._item_ids_by_context = {}

    def update(self):
        delta = AnyList.update(self)
        self._update_item_ids_by_context()
        return delta

    def _update_item_ids_by_context(self):
        item_ids_by_context = defaultdict(list)
        for item_id, item in self.keeplist.iteritems():
            context = item['context']
            item_ids_by_context[context].append(item_id)
        self._item_ids_by_context = dict(item_ids_by_context)

    def list_ids_in_contexts(self, contexts):
        if not cti_context.get('config').part_context():
            return self.keeplist.keys()
        elif not contexts:
            return []
        elif len(contexts) == 1:
            return self._item_ids_by_context.get(contexts[0], [])
        else:
            item_ids = set()
            for context in contexts:
                item_ids.update(self._item_ids_by_context.get(context, []))
            return list(item_ids)

    def get_item_in_contexts(self, item_id, contexts):
        try:
            item = self.keeplist[item_id]
        except KeyError:
            return None
        else:
            if not cti_context.get('config').part_context():
                return item
            elif not contexts:
                return None
            else:
                if item['context'] in contexts:
                    return item
                return None

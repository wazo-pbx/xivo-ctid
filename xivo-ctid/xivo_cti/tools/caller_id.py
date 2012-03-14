# vim: set fileencoding=utf-8 :
# XiVO CTI Server

# Copyright (C) 2007-2011  Avencall'
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re

COMPLETE_CALLER_ID_PATTERN = re.compile('\"(.*)\" \<(\d+)\>')


def build_caller_id(caller_id, name, number):
    if _complete_caller_id(caller_id):
        cid_name, cid_number = COMPLETE_CALLER_ID_PATTERN.search(caller_id).groups()
        return caller_id, cid_name, cid_number
    else:
        return '"%s" <%s>' % (name, number), name, number


def _complete_caller_id(caller_id):
    return True if COMPLETE_CALLER_ID_PATTERN.match(caller_id) else False


def build_agi_caller_id(cid_all, cid_name, cid_number):
    cid = dict()
    (cid_all and cid.update({'CALLERID(all)': cid_all}))
    (cid_name and cid.update({'CALLERID(name)': cid_name}))
    (cid_number and cid.update({'CALLERID(number)': cid_number}))

    return cid

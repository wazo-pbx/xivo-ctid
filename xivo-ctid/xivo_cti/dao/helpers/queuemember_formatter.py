# -*- coding: utf-8 -*-

# XiVO CTI Server
# Copyright (C) 2009-2012  Avencall
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

class QueueMemberFormatter(object):

    @classmethod
    def format_queuemembers(cls, queuemembers):
        ret = {}
        for queuemember in queuemembers:
            key = cls._generate_key(queuemember)
            value = cls._convert_row_to_dict(queuemember)
            ret[key] = value
        return ret

    @staticmethod
    def _generate_key(row):
        key_tuple = (unicode(row.queue_name), unicode(row.interface))
        return str(key_tuple)

    @staticmethod
    def _convert_row_to_dict(row):
        return {
            'queue_name': row.queue_name,
            'interface': row.interface,
            'penalty': row.penalty,
            'call_limit': row.call_limit,
            'paused': row.paused,
            'commented': row.commented,
            'usertype': row.usertype,
            'userid': row.userid,
            'channel': row.channel,
            'category': row.category,
            'skills': row.skills,
            'state_interface': row.state_interface
        }

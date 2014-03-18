# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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

from xivo.caller_id import build_caller_id


class MeetmeDAO(object):

    def __init__(self, innerdata):
        self.innerdata = innerdata

    def get_caller_id_from_context_number(self, context, number):
        name = 'Conference'
        for meetme in self.innerdata.xod_config['meetmes'].keeplist.itervalues():
            if meetme['confno'] == number and meetme['context'] == context:
                name = 'Conference %s' % meetme['name']
                break
        return build_caller_id('', name, number)[0]

# vim: set fileencoding=utf-8 :
# XiVO CTI Server

# Copyright (C) 2007-2011  Avencall
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


from xivo_cti.interfaces import interfaces


class FAGI(interfaces.Interfaces):
    kind = 'FAGI'
    sep = '\n'

    def __init__(self, ctiserver):
        interfaces.Interfaces.__init__(self, ctiserver)
        self.stack = list()

    def connected(self, connid):
        interfaces.Interfaces.connected(self, connid)

    def disconnected(self, cause):
        interfaces.Interfaces.disconnected(self, cause)

    def set_ipbxid(self, ipbxid):
        self.ipbxid = ipbxid
        self.innerdata = self._ctiserver.safe.get(self.ipbxid)

    def manage_connection(self, msg):
        self.stack.extend(msg.split(self.sep))
        if self.stack[-1] == '' and self.stack[-2] == '':
            # that should be when we have received the whole event
            self.agidetails = dict([line.split(': ', 1)
                                    for line in self.stack if line])
            self.channel = self.agidetails.get('agi_channel')
            self.innerdata.fagi_setup(self)
            if self.innerdata.fagi_sync('get', self.channel, 'ami'):
                self.innerdata.fagi_sync('clear', self.channel)
                self.innerdata.fagi_handle(self.channel, 'AGI')
            else:
                self.innerdata.fagi_sync('set', self.channel, 'agi')
        return []

    def reply(self, replylines):
        print 'FAGI reply', replylines

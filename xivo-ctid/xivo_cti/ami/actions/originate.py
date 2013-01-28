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

from xivo_cti.ami.actions.action import AMIAction


class Originate(AMIAction):

    _required_fields = ['channel']
    _optional_dependencies = [('exten', 'context', 'priority'),
                               ('application', 'data')]

    def __init__(self):
        super(Originate, self).__init__()
        self.action = 'Originate'
        self.channel = None
        self.exten = None
        self.context = None
        self.priority = None
        self.application = None
        self.data = None
        self.timeout = None
        self.callerid = None
        self.variable = None
        self.account = None
        self.async = None
        self.codecs = []

    def _get_args(self):
        args = super(Originate, self)._get_args()
        if self.channel:
            args.append(('Channel', self.channel))
        if self.exten:
            args.append(('Exten', self.exten))
        if self.context:
            args.append(('Context', self.context))
        if self.priority:
            args.append(('Priority', self.priority))
        if self.application:
            args.append(('Application', self.application))
        if self.data:
            args.append(('Data', self.data))
        if self.timeout:
            args.append(('Timeout', self.timeout))
        if self.callerid:
            args.append(('CallerID', self.callerid))
        if self.variable:
            args.append(('Variable', self.variable))
        if self.account:
            args.append(('Account', self.account))
        if self.async:
            args.append(('Async', self.async))
        if self.codecs:
            args.append(('Codecs', ','.join(self.codecs)))
        return args

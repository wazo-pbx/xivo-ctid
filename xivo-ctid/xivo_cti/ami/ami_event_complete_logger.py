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

from xivo_cti.ami.ami_logger import AMILogger

log_ami_events_complete = False


class AMIEventCompleteLogger(AMILogger):
    _instance = None
    _log_header = 'AMI event complete logger'
    logged_events = ['CoreShowChannelsComplete',
                     'DAHDIShowChannelsComplete',
                     'MeetmeListComplete',
                     'ParkedCallsComplete',
                     'PeerlistComplete',
                     'QueueStatusComplete',
                     'QueueSummaryComplete',
                     'RegistrationsComplete',
                     'ShowDialPlanComplete',
                     'StatusComplete',
                     'VoicemailUserEntryComplete',
                     ]

    def log_ami_event(self, event):
        if log_ami_events_complete:
            super(AMIEventCompleteLogger, self).log_ami_event(event)

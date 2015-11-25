# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

from xivo_cti.cti.cti_command import CTICommandClass


def _parse(msg, command):
    voicemail = msg['voicemail']
    if not isinstance(voicemail, basestring):
        raise ValueError('expected basestring: was {}'.format(type(voicemail)))
    if not voicemail.isalnum():
        raise ValueError('expected alphanumeric string: was {}'.format(voicemail))

    command.voicemail_number = voicemail


BlindTransferVoicemail = CTICommandClass('blind_transfer_voicemail', None, _parse)
AttendedTransferVoicemail = CTICommandClass('attended_transfer_voicemail', None, _parse)
BlindTransferVoicemail.add_to_registry()
AttendedTransferVoicemail.add_to_registry()

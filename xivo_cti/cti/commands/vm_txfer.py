# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

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

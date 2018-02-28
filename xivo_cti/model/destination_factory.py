# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import re

from xivo_cti.model.consult_voicemail_destination import ConsultVoicemailDestination
from xivo_cti.model.extension_destination import ExtensionDestination
from xivo_cti.model.voicemail_destination import VoicemailDestination

from collections import namedtuple

ParsedURL = namedtuple('ParsedURL', ['destination_type', 'ipbxid', 'value'])


class UnimplementedDestinationException(NotImplementedError):
    pass


class DestinationFactory(object):

    _type_to_class = {
        'exten': ExtensionDestination,
        'voicemail': VoicemailDestination,
        'vm_consult': ConsultVoicemailDestination,
    }
    _url_pattern = re.compile(r'(\w+):(\w+)/(.+)')

    @classmethod
    def make_from(cls, url):
        parsed_url = cls._parse(url)
        if parsed_url.destination_type not in cls._type_to_class:
            msg = 'Unimplemented type {0}'.format(parsed_url.destination_type)
            raise UnimplementedDestinationException(msg)
        return cls._type_to_class[parsed_url.destination_type](*parsed_url)

    @classmethod
    def is_destination_url(cls, url):
        return cls._url_pattern.match(url) is not None

    @classmethod
    def _parse(cls, url):
        result = cls._url_pattern.match(url)
        if not result:
            raise ValueError('Input does not match the URL pattern %s', url)
        return ParsedURL(result.group(1), result.group(2), result.group(3))

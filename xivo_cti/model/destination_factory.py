# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

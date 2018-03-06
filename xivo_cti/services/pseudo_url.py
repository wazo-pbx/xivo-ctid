# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import re

from xivo_cti.model.destination import Destination


class PseudoURL(object):

    'voicemail:xivo/123'
    url_pattern = re.compile(r'(\w+):(\w+)/(\d+)')

    @classmethod
    def parse(cls, url):
        result = cls.url_pattern.match(url)
        if not result:
            raise ValueError('Input does not match the URL pattern %s', url)
        return Destination(result.group(1), result.group(2), result.group(3))

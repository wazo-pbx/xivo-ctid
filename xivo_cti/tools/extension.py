# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import re
import logging
from xivo import caller_id

logger = logging.getLogger('extension')

VALID_EXTENSION_PATTERN = re.compile('[^a-z0-9#*+]', re.I)


class InvalidExtension(ValueError):
    def __init__(self, exten):
        super(InvalidExtension, self).__init__()
        self.exten = exten


def normalize_exten(exten):
    try:
        extentodial = caller_id.extract_number(exten)
    except ValueError:
        extentodial = re.sub(VALID_EXTENSION_PATTERN, '', exten)

    if not extentodial:
        raise InvalidExtension(exten)

    return extentodial

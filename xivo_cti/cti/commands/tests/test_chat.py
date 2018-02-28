# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import assert_that, equal_to
from uuid import uuid4

from ..chat import Chat

msg = u'''\
A multi line
message with some accentuàtéd
characters'''


class TestChat(unittest.TestCase):

    def test_from_dict(self):
        xivo_uuid, user_uuid = str(uuid4()), str(uuid4())

        cti_msg = {'class': 'chitchat',
                   'alias': u'pépé',
                   'to': [xivo_uuid, user_uuid],
                   'text': msg,
                   'commandid': '124.1245'}

        chat = Chat.from_dict(cti_msg)

        assert_that(chat.alias, equal_to(u'pépé'))
        assert_that(chat.remote_xivo_uuid, equal_to(xivo_uuid))
        assert_that(chat.remote_user_uuid, equal_to(user_uuid))
        assert_that(chat.text, equal_to(msg))

    def test_from_dict_with_an_invalid_xivo_uuid(self):
        xivo_uuid, user_id = 'lol', str(uuid4())

        cti_msg = {'class': 'chitchat',
                   'alias': u'pépé',
                   'to': [xivo_uuid, user_id],
                   'text': msg,
                   'commandid': '124.1245'}

        self.assertRaises(ValueError, Chat.from_dict, cti_msg)

    def test_from_dict_with_an_invalid_user_uuid(self):
        xivo_uuid, user_uuid = str(uuid4()), 'lol'

        cti_msg = {'class': 'chitchat',
                   'alias': u'pépé',
                   'to': [xivo_uuid, user_uuid],
                   'text': msg,
                   'commandid': '124.1245'}

        self.assertRaises(ValueError, Chat.from_dict, cti_msg)

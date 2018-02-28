# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock, patch
from xivo_bus import Publisher

from xivo_cti.bus_listener import BusListener
from xivo_cti.ctiserver import CTIServer
from xivo_cti.task_queue import _TaskQueue as TaskQueue

from ..chat import ChatPublisher


class TestChatPublisher(unittest.TestCase):

    def setUp(self):
        self.bus_publisher = Mock(Publisher)
        self.bus_listener = Mock(BusListener)
        self.cti_server = Mock(CTIServer)
        self.task_queue = Mock(TaskQueue)

        self.chat_publisher = ChatPublisher(self.bus_publisher,
                                            self.bus_listener,
                                            self.cti_server,
                                            self.task_queue,
                                            'local-xivo-uuid')

    @patch('xivo_cti.services.chat.dao.user')
    def test_deliver_chat_message(self, user_dao):
        user_uuid = '7f523550-03cf-4dac-a858-cb8afdb34775'
        user_id = 42
        from_ = ('other-xivo-uuid', 5)
        to = ('local-xivo-uuid', user_uuid)
        alias = u'Föobar'
        text = u'a chat messagé'

        user_dao.get_by_uuid.return_value = {'id': user_id}

        self.chat_publisher.deliver_chat_message(from_, to, alias, text)

        expected_destination = '{}/{}'.format('local-xivo-uuid', user_id)
        expected_message = {'class': 'chitchat',
                            'alias': alias,
                            'to': to,
                            'from': from_,
                            'text': text}
        self.cti_server.send_to_cti_client.assert_called_once_with(
            expected_destination, expected_message)

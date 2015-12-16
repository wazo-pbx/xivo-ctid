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

import unittest

from mock import Mock
from xivo_bus import Publisher
from xivo_bus.resources.chat.event import ChatMessageEvent

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

    def test_that_messages_are_published_on_the_bus(self):
        from_user_id = 42
        to_user_id = 23
        to_xivo_uuid = 'a-valid-uuid'
        alias = u'Bõb'
        text = 'a message'

        expected_msg = ChatMessageEvent(('local-xivo-uuid', from_user_id),
                                        (to_xivo_uuid, to_user_id),
                                        alias, text)

        self.chat_publisher.on_cti_chat_message(from_user_id, to_xivo_uuid, to_user_id, alias, text)

        self.bus_publisher.publish.assert_called_once_with(expected_msg)

    def test_deliver_chat_message(self):
        from_ = ('other-xivo-uuid', 5)
        to = ('local-xivo-uuid', 42)
        alias = u'Föobar'
        text = u'a chat messagé'

        self.chat_publisher.deliver_chat_message(from_, to, alias, text)

        expected_destination = '{}/{}'.format(*to)
        expected_message = {'class': 'chitchat',
                            'alias': alias,
                            'to': to,
                            'from': from_,
                            'text': text}
        self.cti_server.send_to_cti_client.assert_called_once_with(
            expected_destination, expected_message)

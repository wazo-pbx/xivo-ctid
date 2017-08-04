# -*- coding: utf-8 -*-

# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
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

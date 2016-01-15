# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016 Avencall
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

from concurrent import futures
from hamcrest import assert_that, equal_to
from mock import Mock
from mock import patch
from mock import sentinel as s

from xivo_cti.async_runner import AsyncRunner
from xivo_cti.task_queue import new_task_queue
from xivo_cti.ctiserver import CTIServer
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.interfaces.interface_cti import NotLoggedException
from xivo_cti.cti.cti_message_codec import (CTIMessageDecoder,
                                            CTIMessageEncoder)


class TestCTI(unittest.TestCase):

    def setUp(self):
        self.task_queue = new_task_queue()
        self.async_runner = AsyncRunner(futures.ThreadPoolExecutor(max_workers=1), self.task_queue)
        self._ctiserver = Mock(CTIServer, myipbxid='xivo')

        with patch('xivo_cti.interfaces.interface_cti.context', Mock()):
            with patch('xivo_cti.interfaces.interface_cti.AuthentificationHandler', Mock()):
                self._cti_connection = CTI(self._ctiserver, CTIMessageDecoder(), CTIMessageEncoder())
        self._cti_connection.login_task = Mock()

    def test_user_id_not_connected(self):
        self.assertRaises(NotLoggedException, self._cti_connection.user_id)

    def test_user_id(self):
        user_id = 5
        self._cti_connection.connection_details['userid'] = user_id

        result = self._cti_connection.user_id()

        self.assertEqual(result, user_id)

    def test_on_auth_success(self):
        with patch.object(self._cti_connection, '_auth_handler') as auth_handler:
            with patch.object(self._cti_connection, '_get_answer_cb') as get_answer_cb:
                self._cti_connection._on_auth_success()

                get_answer_cb.assert_called_once_with(auth_handler.user_id.return_value)

                expected = {'userid': auth_handler.user_id.return_value,
                            'user_uuid': auth_handler.user_uuid.return_value,
                            'auth_token': auth_handler.auth_token.return_value,
                            'authenticated': auth_handler.is_authenticated.return_value,
                            'ipbxid': 'xivo'}
                assert_that(self._cti_connection.connection_details, equal_to(expected))

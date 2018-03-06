# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from concurrent import futures
from hamcrest import assert_that, calling, equal_to, raises
from mock import Mock
from mock import patch

from xivo_cti.async_runner import AsyncRunner
from xivo_cti.task_queue import new_task_queue
from xivo_cti.ctiserver import CTIServer
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.interfaces.interface_cti import NotLoggedException
from xivo_cti.cti.cti_message_codec import (CTIMessageDecoder,
                                            CTIMessageEncoder)
from xivo_cti.cti.cti_group import CTIGroup


SOME_USER_ID = 5


class TestCTI(unittest.TestCase):

    def setUp(self):
        self.task_queue = new_task_queue()
        self.async_runner = AsyncRunner(futures.ThreadPoolExecutor(max_workers=1), self.task_queue)
        self._ctiserver = Mock(CTIServer, myipbxid='xivo')
        self._broadcast_cti_group = Mock(CTIGroup)

        with patch('xivo_cti.interfaces.interface_cti.context', Mock()):
            with patch('xivo_cti.interfaces.interface_cti.AuthenticationHandler', Mock()):
                self._cti_connection = CTI(self._ctiserver,
                                           self._broadcast_cti_group,
                                           CTIMessageDecoder(),
                                           CTIMessageEncoder())
        self._cti_connection.login_task = Mock()

    def test_user_id_not_connected(self):
        self.assertRaises(NotLoggedException, self._cti_connection.user_id)

    def test_user_id(self):
        user_id = SOME_USER_ID
        self._cti_connection.connection_details['userid'] = user_id

        result = self._cti_connection.user_id()

        self.assertEqual(result, user_id)

    def test_on_auth_success(self):
        with patch.object(self._cti_connection, '_auth_handler') as auth_handler:
            with patch.object(self._cti_connection, '_update_answer_cb') as update_answer_cb:
                self._cti_connection._on_auth_success()

                self._broadcast_cti_group.add.assert_called_once_with(self._cti_connection)
                update_answer_cb.assert_called_once_with(auth_handler.user_id.return_value)

                expected = {'userid': auth_handler.user_id.return_value,
                            'user_uuid': auth_handler.user_uuid.return_value,
                            'auth_token': auth_handler.auth_token.return_value,
                            'authenticated': auth_handler.is_authenticated.return_value,
                            'ipbxid': 'xivo'}
                assert_that(self._cti_connection.connection_details, equal_to(expected))

    def test_disconnected_invalid_cause(self):
        self._cti_connection.connection_details['userid'] = SOME_USER_ID
        with patch('xivo_cti.interfaces.interface_cti.context', Mock()):
            with patch('xivo_cti.interfaces.interface_cti.AuthenticationHandler', Mock()):
                assert_that(calling(self._cti_connection.disconnected).with_args('invalid_cause'), raises(TypeError))

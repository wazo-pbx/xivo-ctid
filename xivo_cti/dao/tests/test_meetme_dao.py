# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock
from xivo_cti import innerdata
from xivo_cti.dao import meetme_dao


class TestMeetmeDAO(unittest.TestCase):

    def setUp(self):
        self.innerdata = Mock(innerdata.Safe)

    def test_get_caller_id_from_context_number(self):
        number = '4001'
        context = 'myctx'
        name = 'Super conference'

        meetme_config = Mock()
        meetme_config.keeplist = {
            '3': {
                'confno': number,
                'context': context,
                'name': name,
            },
            '5': {
                'confno': '543',
                'context': context,
                'name': 'Another meetme',
            }
        }
        self.innerdata.xod_config = {
            'meetmes': meetme_config
        }

        expected_caller_id = '"Conference %s" <%s>' % (name, number)

        dao = meetme_dao.MeetmeDAO(self.innerdata)

        caller_id = dao.get_caller_id_from_context_number(context, number)

        self.assertEqual(caller_id, expected_caller_id)

    def test_get_caller_id_from_context_number_unknown(self):
        number = '666'
        meetme_config = Mock()
        meetme_config.keeplist = {
            '5': {
                'confno': '543',
                'context': 'default',
                'name': 'Another meetme',
            }
        }
        self.innerdata.xod_config = {
            'meetmes': meetme_config
        }

        expected_caller_id = '"Conference" <%s>' % number

        dao = meetme_dao.MeetmeDAO(self.innerdata)

        caller_id = dao.get_caller_id_from_context_number('default', number)

        self.assertEqual(caller_id, expected_caller_id)

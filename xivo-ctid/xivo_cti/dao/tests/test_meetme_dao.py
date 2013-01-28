# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

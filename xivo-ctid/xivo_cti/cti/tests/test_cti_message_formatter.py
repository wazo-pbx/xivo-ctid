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

from hamcrest import assert_that
from hamcrest import equal_to
from xivo_cti.services.agent.status import AgentStatus
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter

CLASS = 'class'


class TestCTIMessageFormatter(unittest.TestCase):

    def test_update_agent_status(self):
        agent_id = 42
        agent_status = {'availability': AgentStatus.logged_out,
                        'availability_since': 123456789}
        expected_result = {'class': 'getlist',
                           'listname': 'agents',
                           'function': 'updatestatus',
                           'tipbxid': 'xivo',
                           'tid': agent_id,
                           'status': agent_status}
        cti_message_formatter = CTIMessageFormatter()

        result = cti_message_formatter.update_agent_status(agent_id, agent_status)

        self.assertEqual(result, expected_result)

    def test_report_ipbxcommand_error(self):
        msg = 'Ad libitum'
        expected = {
            CLASS: 'ipbxcommand',
            'error_string': msg,
        }

        result = CTIMessageFormatter.ipbxcommand_error(msg)

        assert_that(result, equal_to(expected), 'Error message')

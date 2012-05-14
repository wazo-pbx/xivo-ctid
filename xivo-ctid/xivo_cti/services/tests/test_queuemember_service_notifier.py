#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2011  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import Queue
from tests.mock import Mock, call, ANY
from xivo_cti.services.queuemember_service_notifier import QueueMemberServiceNotifier
from xivo_cti.tools.delta_computer import DictDelta
from xivo_cti.statistics.queuestatisticsproducer import QueueStatisticsProducer
from xivo_cti.services.queue_service_manager import NotAQueueException

class TestQueueMemberServiceNotifier(unittest.TestCase):

    def setUp(self):
        self.ipbx_id = 'xivo_test'
        self.notifier = QueueMemberServiceNotifier()
        self.notifier.ipbx_id = self.ipbx_id
        self.notifier.innerdata_dao = Mock()
        self.notifier.events_cti = Queue.Queue()
        self.queue_statistics_producer = Mock(QueueStatisticsProducer)
        self.notifier.queue_statistics_producer = self.queue_statistics_producer
        self.callback = Mock()
        self.notifier._callbacks.append(self.callback)

    def test_queuemember_config_updated_add(self):
        input_delta = DictDelta({'Agent/2345,service':
                                    {'queue_name':'service', 'interface':'Agent/2345'},
                                 'Agent/2309,service':
                                    {'queue_name':'service', 'interface':'Agent/2309'}
                                 }, {}, {})
        queuemembers_to_add = ['Agent/2309,service', 'Agent/2345,service']

        self.notifier.innerdata_dao.get_queue_id.return_value = '34'

        self.notifier.queuemember_config_updated(input_delta)

        self.notifier.innerdata_dao.apply_queuemember_delta.assert_called_once_with(input_delta)
        cti_event = self.notifier.events_cti.get()
        self._assert_cti_event_is_addconfig_queuemembers_for(cti_event, queuemembers_to_add)

        self.queue_statistics_producer.on_agent_added.assert_was_called_with('34', 'Agent/2345')
        self.queue_statistics_producer.on_agent_added.assert_was_called_with('34', 'Agent/2309')

        self.notifier.innerdata_dao.get_queue_id.assert_called_with('service')

        self.callback.assert_called_once_with(input_delta)


    def test_queuemember_config_updated_add_in_group(self):
        input_delta = DictDelta({'SIP/2345,group':
                                    {'queue_name':'group', 'interface':'SIP/2345'}
                                 }, {}, {})
        expected_cti_event = {'class': 'getlist',
                              'function': 'addconfig',
                              'listname': 'queuemembers',
                              'list': ['SIP/2345,group'],
                              'tipbxid': self.ipbx_id
                              }
        self.notifier.innerdata_dao.get_queue_id.side_effect = NotAQueueException

        self.notifier.queuemember_config_updated(input_delta)

        self.notifier.innerdata_dao.apply_queuemember_delta.assert_called_once_with(input_delta)
        cti_event = self.notifier.events_cti.get()
        self.assertEqual(cti_event, expected_cti_event)

        self.queue_statistics_producer.on_agent_added.assert_never_called()

        self.notifier.innerdata_dao.get_queue_id.assert_called_with('group')

        self.callback.assert_called_once_with(input_delta)


    def test_queuemember_deleted(self):
        input_delta = DictDelta({}, {}, {'Agent/2345,service':
                                    {'queue_name':'service', 'interface':'Agent/2345'},
                                 'Agent/2309,service':
                                    {'queue_name':'service', 'interface':'Agent/2309'}})

        self.notifier.innerdata_dao.get_queue_id.return_value = '34'

        self.notifier.queuemember_config_updated(input_delta)

        self.notifier.innerdata_dao.apply_queuemember_delta.assert_called_once_with(input_delta)
        cti_event = self.notifier.events_cti.get()
        self._assert_cti_event_is_delconfig_queuemembers_for(cti_event, ['Agent/2345,service', 'Agent/2309,service'])

        self.queue_statistics_producer.on_agent_removed.assert_was_called_with('34', 'Agent/2345')
        self.queue_statistics_producer.on_agent_removed.assert_was_called_with('34', 'Agent/2309')

        self.notifier.innerdata_dao.get_queue_id.assert_called_with('service')

        self.callback.assert_called_once_with(input_delta)

    def test_queuemember_config_updated_change(self):
        input_delta = DictDelta({}, {'key1': 'value1', 'key2': 'value2'}, {})
        expected_cti_events = [{'class': 'getlist',
                                'function': 'updateconfig',
                                'listname': 'queuemembers',
                                'config': 'value1',
                                'tid': 'key1',
                                'tipbxid': self.ipbx_id},
                               {'class': 'getlist',
                                'function': 'updateconfig',
                                'listname': 'queuemembers',
                                'config': 'value2',
                                'tid': 'key2',
                                'tipbxid': self.ipbx_id}]

        self.notifier.queuemember_config_updated(input_delta)

        innerdata_method_calls = self.notifier.innerdata_dao.method_calls
        cti_events = []
        while not self.notifier.events_cti.empty():
            cti_events.append(self.notifier.events_cti.get())
        self.assertEqual(innerdata_method_calls, [call.apply_queuemember_delta(ANY)])
        self.assertEqual(cti_events.sort(), expected_cti_events.sort())

        self.callback.assert_called_once_with(input_delta)

    def test_request_queuemembers_to_ami_empty(self):
        queuemembers_list = []
        self.notifier.interface_ami = Mock()
        expected_ami_method_calls = []

        self.notifier.request_queuemembers_to_ami(queuemembers_list)

        ami_method_calls = self.notifier.interface_ami.method_calls
        self.assertEqual(ami_method_calls, expected_ami_method_calls)

    def test_request_queuemembers_to_ami_full(self):
        queuemembers_list = [('agent1', 'queue1'), ('agent2', 'queue2')]
        params1 = {'mode': 'request_queuemember',
                   'amicommand': 'sendcommand',
                   'amiargs': ('queuestatus', [('Member', 'agent1'),
                                               ('Queue', 'queue1')])}
        params2 = {'mode': 'request_queuemember',
                   'amicommand': 'sendcommand',
                   'amiargs': ('queuestatus', [('Member', 'agent2'),
                                               ('Queue', 'queue2')])}
        self.notifier.interface_ami = Mock()
        expected_ami_method_calls = [call.execute_and_track(ANY, params1),
                                     call.execute_and_track(ANY, params2)]

        self.notifier.request_queuemembers_to_ami(queuemembers_list)

        ami_method_calls = self.notifier.interface_ami.method_calls
        self.assertEqual(ami_method_calls, expected_ami_method_calls)

    def test_subscribe(self):
        function = Mock()

        self.notifier.subscribe(function)

        self.assertTrue(function in self.notifier._callbacks)

    def _assert_cti_event_is_addconfig_queuemembers_for(self, cti_event, queuemembers_to_add):
        self._assert_cti_event_headers(cti_event, 'addconfig')
        self._assert_equivalent_lists(cti_event['list'], queuemembers_to_add, 'the list of queuemembers to add is invalid')

    def _assert_cti_event_is_delconfig_queuemembers_for(self, cti_event, queuemembers_to_remove):
        self._assert_cti_event_headers(cti_event, 'delconfig')
        self._assert_equivalent_lists(cti_event['list'], queuemembers_to_remove, 'the list of queuemembers to remove is invalid')

    def _assert_cti_event_headers(self, cti_event, function):
        self.assertEqual(cti_event['class'], 'getlist')
        self.assertEqual(cti_event['function'], function)
        self.assertEqual(cti_event['listname'], 'queuemembers')
        self.assertEqual(cti_event['tipbxid'], self.ipbx_id)

    def _assert_equivalent_lists(self, list_to_compare, expected_list, msg=None):
        list_to_compare.sort()
        expected_list.sort()
        self.assertEqual(list_to_compare, expected_list, msg)

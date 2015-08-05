# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
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
from mock import Mock, sentinel
from xivo_cti.services.agent.status import AgentStatus
from xivo_cti.services.queue_member.member import QueueMember
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter

CLASS = 'class'


class TestCTIMessageFormatter(unittest.TestCase):

    def test_add_queue_members(self):
        queue_member_ids = xrange(1, 4)
        expected_result = {
            'class': 'getlist',
            'listname': 'queuemembers',
            'function': 'addconfig',
            'tipbxid': 'xivo',
            'list': [1, 2, 3],
        }

        result = CTIMessageFormatter.add_queue_members(queue_member_ids)

        self.assertEqual(result, expected_result)

    def test_delete_queue_members(self):
        queue_member_ids = xrange(1, 4)
        expected = {
            'class': 'getlist',
            'listname': 'queuemembers',
            'function': 'delconfig',
            'tipbxid': 'xivo',
            'list': [1, 2, 3],
        }

        result = CTIMessageFormatter.delete_queue_members(queue_member_ids)

        self.assertEqual(result, expected)

    def test_update_queue_member_config(self):
        queue_member = Mock(QueueMember, id=12)
        queue_member.to_cti_config.return_value = sentinel.config
        expected = {
            'class': 'getlist',
            'listname': 'queuemembers',
            'function': 'updateconfig',
            'tipbxid': 'xivo',
            'tid': 12,
            'config': sentinel.config,
        }

        result = CTIMessageFormatter.update_queue_member_config(queue_member)

        self.assertEqual(result, expected)

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

        result = CTIMessageFormatter.update_agent_status(agent_id, agent_status)

        self.assertEqual(result, expected_result)

    def test_report_ipbxcommand_error(self):
        msg = 'Ad libitum'
        expected = {
            CLASS: 'ipbxcommand',
            'error_string': msg,
        }

        result = CTIMessageFormatter.ipbxcommand_error(msg)

        assert_that(result, equal_to(expected), 'Error message')

    def test_dial_success(self):
        expected = {
            'class': 'dial_success',
            'exten': sentinel.exten,
        }

        result = CTIMessageFormatter.dial_success(sentinel.exten)

        assert_that(result, equal_to(expected))

    def test_people_headers_result(self):
        headers = {
            'column_headers': sentinel.headers,
            'column_types': sentinel.types
        }
        expected = {
            'class': 'people_headers_result',
            'column_headers': sentinel.headers,
            'column_types': sentinel.types
        }

        result = CTIMessageFormatter.people_headers_result(headers)

        assert_that(result, equal_to(expected))

    def test_people_search_result(self):
        search_result = {
            "term": "Bob",
            "column_headers": ["Firstname", "Lastname", "Phone number", "Mobile", "Fax", "Email", "Agent"],
            "column_types": [None, "name", "number_office", "number_mobile", "fax", "email", "relation_agent"],
            "results": [
                {
                    "column_values": ["Bob", "Marley", "5555555", "5556666", "5553333", "mail@example.com", None],
                    "relations": {
                        "agent": None,
                        "user": None,
                        "endpoint": None
                    },
                    "source": "my_ldap_directory"
                }, {
                    "column_values": ["Charlie", "Boblin", "5555556", "5554444", "5552222", "mail2@example.com", None],
                    "relations": {
                        "agent": {
                            "id": 12,
                            "xivo_id": "ad2f36c7-b0f3-48da-a63c-37434fed479b"
                        },
                        "user": {
                            "id": 34,
                            "xivo_id": "ad2f36c7-b0f3-48da-a63c-37434fed479b"
                        },
                        "endpoint": {
                            "id": 56,
                            "xivo_id": "ad2f36c7-b0f3-48da-a63c-37434fed479b"
                        },
                    },
                    "source": "internal"
                }
            ]
        }

        result = CTIMessageFormatter.people_search_result(search_result)

        expected = dict(search_result)
        expected.update({'class': 'people_search_result'})

        assert_that(result, equal_to(expected))

    def test_people_favorites_result(self):
        favorites_result = {
            "column_headers": ["Firstname", "Lastname", "Phone number", "Mobile", "Fax", "Email",
                               "Agent", "Favorite"],
            "column_types": [None, "name", "number_office", "number_mobile", "fax", "email",
                             "relation_agent", "favorite"],
            "results": [
                {
                    "column_values": ["Bob", "Marley", "5555555", "5556666", "5553333",
                                      "mail@example.com", None, True],
                    "relations": {
                        "agent": None,
                        "user": None,
                        "endpoint": None
                    },
                    "source": "my_ldap_directory"
                }, {
                    "column_values": ["Charlie", "Boblin", "5555556", "5554444", "5552222",
                                      "mail2@example.com", None, True],
                    "relations": {
                        "agent": {
                            "id": 12,
                            "xivo_id": "ad2f36c7-b0f3-48da-a63c-37434fed479b"
                        },
                        "user": {
                            "id": 34,
                            "xivo_id": "ad2f36c7-b0f3-48da-a63c-37434fed479b"
                        },
                        "endpoint": {
                            "id": 56,
                            "xivo_id": "ad2f36c7-b0f3-48da-a63c-37434fed479b"
                        },
                    },
                    "source": "internal"
                }
            ]
        }

        result = CTIMessageFormatter.people_favorites_result(favorites_result)

        expected = dict(favorites_result)
        expected.update({'class': 'people_favorites_result'})

        assert_that(result, equal_to(expected))

    def test_people_personal_contacts_result(self):
        personal_contacts_result = {
            "column_headers": ["Firstname", "Lastname", "Phone number", "Mobile", "Fax", "Email",
                               "Agent", "Favorite", "Personal"],
            "column_types": [None, "name", "number_office", "number_mobile", "fax", "email",
                             "relation_agent", "favorite", "personal"],
            "results": [
                {
                    "column_values": ["Bob", "Marley", "5555555", "5556666", "5553333",
                                      "mail@example.com", None, True, True],
                    "relations": {
                        "agent": None,
                        "user": None,
                        "endpoint": None
                    },
                    "source": "personal"
                }, {
                    "column_values": ["Charlie", "Boblin", "5555556", "5554444", "5552222",
                                      "mail2@example.com", None, False, True],
                    "relations": {
                        "agent": None,
                        "user": None,
                        "endpoint": None
                    },
                    "source": "personal"
                }
            ]
        }

        result = CTIMessageFormatter.people_personal_contacts_result(personal_contacts_result)

        expected = dict(personal_contacts_result)
        expected.update({'class': 'people_personal_contacts_result'})

        assert_that(result, equal_to(expected))

    def test_people_favorite_update(self):
        source = "internal"
        source_entry_id = "123456789"
        enabled = True
        set_favorite_result = {
            'class': 'people_favorite_update',
            'data': {
                'source': source,
                'source_entry_id': source_entry_id,
                'favorite': enabled,
            }
        }

        result = CTIMessageFormatter.people_favorite_update(source, source_entry_id, enabled)

        expected = dict(set_favorite_result)
        expected.update({'class': 'people_favorite_update'})

        assert_that(result, equal_to(expected))

    def test_people_personal_contact_created(self):
        expected = {
            'class': 'people_personal_contact_created'
        }

        result = CTIMessageFormatter.people_personal_contact_created()

        assert_that(result, equal_to(expected))

    def test_people_personal_contact_deleted(self):
        source = "personal"
        source_entry_id = "123456789"
        expected = {
            'class': 'people_personal_contact_deleted',
            'data': {
                'source': source,
                'source_entry_id': source_entry_id
            }
        }

        result = CTIMessageFormatter.people_personal_contact_deleted(source, source_entry_id)

        assert_that(result, equal_to(expected))

    def test_people_personal_contact_raw_update(self):
        source = "personal"
        source_entry_id = "123456789"
        expected = {
            'class': 'people_personal_contact_raw_update',
            'data': {
                'source': source,
                'source_entry_id': source_entry_id,
            }
        }

        result = CTIMessageFormatter.people_personal_contact_raw_update(source, source_entry_id)

        assert_that(result, equal_to(expected))

    def test_people_personal_contact_raw_result(self):
        source = "personal"
        source_entry_id = "123456789"
        contact_infos = {
            'firstname': 'Bob',
            'lastname': 'The Builder'
            }
        expected = {
            'class': 'people_personal_contact_raw_result',
            'data': {
                'source': source,
                'source_entry_id': source_entry_id,
                'firstname': 'Bob',
                'lastname': 'The Builder'
            }
        }

        result = CTIMessageFormatter.people_personal_contact_raw_result(source, source_entry_id, contact_infos)

        assert_that(result, equal_to(expected))

    def test_update_phone_hinstatus(self):
        hint = 8
        phone_id = '42'

        result = CTIMessageFormatter.phone_hintstatus_update(phone_id, hint)

        assert_that(result, equal_to({'class': 'getlist',
                                      'listname': 'phones',
                                      'function': 'updatestatus',
                                      'tipbxid': 'xivo',
                                      'tid': phone_id,
                                      'status': {'hintstatus': hint}}))

    def test_agent_status_update(self):
        key = ('xivo-uuid', 42)
        status = 'logged_out'

        result = CTIMessageFormatter.agent_status_update(key, status)

        assert_that(result, equal_to({
            'class': 'agent_status_update',
            'data': {
                'xivo_uuid': 'xivo-uuid',
                'agent_id': 42,
                'status': 'logged_out',
            }
        }))

    def test_endpoint_status_update(self):
        key = ('xivo-uuid', 42)
        status = 0

        result = CTIMessageFormatter.endpoint_status_update(key, status)

        assert_that(result, equal_to({
            'class': 'endpoint_status_update',
            'data': {
                'xivo_uuid': 'xivo-uuid',
                'endpoint_id': 42,
                'status': 0,
            }
        }))

    def test_user_status_update(self):
        key = ('xivo-uuid', 42)
        status = 'busy'

        result = CTIMessageFormatter.user_status_update(key, status)

        assert_that(result, equal_to({
            'class': 'user_status_update',
            'data': {
                'xivo_uuid': 'xivo-uuid',
                'user_id': 42,
                'status': status,
            }
        }))

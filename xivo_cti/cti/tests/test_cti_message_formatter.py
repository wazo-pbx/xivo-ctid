# -*- coding: utf-8 -*-
# Copyright 2007-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

import xivo_cti

from hamcrest import assert_that
from hamcrest import equal_to
from mock import Mock, sentinel as s
from xivo_cti.services.agent.status import AgentStatus
from xivo_cti.services.queue_member.member import QueueMember
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter


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
        queue_member.to_cti_config.return_value = s.config
        expected = {
            'class': 'getlist',
            'listname': 'queuemembers',
            'function': 'updateconfig',
            'tipbxid': 'xivo',
            'tid': 12,
            'config': s.config,
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
            'class': 'ipbxcommand',
            'error_string': msg,
        }

        result = CTIMessageFormatter.ipbxcommand_error(msg)

        assert_that(result, equal_to(expected), 'Error message')

    def test_login_id(self):
        expected = {'class': 'login_id',
                    'sessionid': s.session_id,
                    'wazoversion': xivo_cti.CTI_PROTOCOL_VERSION}

        result = CTIMessageFormatter.login_id(s.session_id)

        assert_that(result, equal_to(expected))

    def test_login_pass(self):
        expected = {'class': 'login_pass',
                    'capalist': [s.cti_profile_id]}

        result = CTIMessageFormatter.login_pass(s.cti_profile_id)

        assert_that(result, equal_to(expected))

    def test_dial_success(self):
        expected = {
            'class': 'dial_success',
            'exten': s.exten,
        }

        result = CTIMessageFormatter.dial_success(s.exten)

        assert_that(result, equal_to(expected))

    def test_people_headers_result(self):
        headers = {
            'column_headers': s.headers,
            'column_types': s.types
        }
        expected = {
            'class': 'people_headers_result',
            'column_headers': s.headers,
            'column_types': s.types
        }

        result = CTIMessageFormatter.people_headers_result(headers)

        assert_that(result, equal_to(expected))

    def test_people_search_result(self):
        search_result = {
            'term': 'Bob',
            'column_headers': ['Firstname', 'Lastname', 'Phone number', 'Mobile', 'Fax', 'Email', 'Agent'],
            'column_types': [None, 'name', 'number_office', 'number_mobile', 'fax', 'email', 'relation_agent'],
            'results': [
                {
                    'column_values': ['Bob', 'Marley', '5555555', '5556666', '5553333', 'mail@example.com', None],
                    'relations': {
                        'agent': None,
                        'user': None,
                        'endpoint': None
                    },
                    'source': 'my_ldap_directory'
                }, {
                    'column_values': ['Charlie', 'Boblin', '5555556', '5554444', '5552222', 'mail2@example.com', None],
                    'relations': {
                        'agent': {
                            'id': 12,
                            'xivo_id': 'ad2f36c7-b0f3-48da-a63c-37434fed479b'
                        },
                        'user': {
                            'id': 34,
                            'xivo_id': 'ad2f36c7-b0f3-48da-a63c-37434fed479b'
                        },
                        'endpoint': {
                            'id': 56,
                            'xivo_id': 'ad2f36c7-b0f3-48da-a63c-37434fed479b'
                        },
                    },
                    'source': 'internal'
                }
            ]
        }

        result = CTIMessageFormatter.people_search_result(search_result)

        expected = dict(search_result)
        expected.update({'class': 'people_search_result'})

        assert_that(result, equal_to(expected))

    def test_people_favorites_result(self):
        favorites_result = {
            'column_headers': ['Firstname', 'Lastname', 'Phone number', 'Mobile', 'Fax', 'Email',
                               'Agent', 'Favorite'],
            'column_types': [None, 'name', 'number_office', 'number_mobile', 'fax', 'email',
                             'relation_agent', 'favorite'],
            'results': [
                {
                    'column_values': ['Bob', 'Marley', '5555555', '5556666', '5553333',
                                      'mail@example.com', None, True],
                    'relations': {
                        'agent': None,
                        'user': None,
                        'endpoint': None
                    },
                    'source': 'my_ldap_directory'
                }, {
                    'column_values': ['Charlie', 'Boblin', '5555556', '5554444', '5552222',
                                      'mail2@example.com', None, True],
                    'relations': {
                        'agent': {
                            'id': 12,
                            'xivo_id': 'ad2f36c7-b0f3-48da-a63c-37434fed479b'
                        },
                        'user': {
                            'id': 34,
                            'xivo_id': 'ad2f36c7-b0f3-48da-a63c-37434fed479b'
                        },
                        'endpoint': {
                            'id': 56,
                            'xivo_id': 'ad2f36c7-b0f3-48da-a63c-37434fed479b'
                        },
                    },
                    'source': 'internal'
                }
            ]
        }

        result = CTIMessageFormatter.people_favorites_result(favorites_result)

        expected = dict(favorites_result)
        expected.update({'class': 'people_favorites_result'})

        assert_that(result, equal_to(expected))

    def test_people_personal_contacts_result(self):
        personal_contacts_result = {
            'column_headers': ['Firstname', 'Lastname', 'Phone number', 'Mobile', 'Fax', 'Email',
                               'Agent', 'Favorite', 'Personal'],
            'column_types': [None, 'name', 'number_office', 'number_mobile', 'fax', 'email',
                             'relation_agent', 'favorite', 'personal'],
            'results': [
                {
                    'column_values': ['Bob', 'Marley', '5555555', '5556666', '5553333',
                                      'mail@example.com', None, True, True],
                    'relations': {
                        'agent': None,
                        'user': None,
                        'endpoint': None
                    },
                    'source': 'personal'
                }, {
                    'column_values': ['Charlie', 'Boblin', '5555556', '5554444', '5552222',
                                      'mail2@example.com', None, False, True],
                    'relations': {
                        'agent': None,
                        'user': None,
                        'endpoint': None
                    },
                    'source': 'personal'
                }
            ]
        }

        result = CTIMessageFormatter.people_personal_contacts_result(personal_contacts_result)

        expected = dict(personal_contacts_result)
        expected.update({'class': 'people_personal_contacts_result'})

        assert_that(result, equal_to(expected))

    def test_people_personal_contacts_purged(self):
        result = CTIMessageFormatter.people_personal_contacts_purged()

        expected = {'class': 'people_personal_contacts_purged'}

        assert_that(result, equal_to(expected))

    def test_people_favorite_update(self):
        source = 'internal'
        source_entry_id = '123456789'
        enabled = True
        set_favorite_result = {
            'class': 'people_favorite_update',
            'source': source,
            'source_entry_id': source_entry_id,
            'favorite': enabled
        }

        result = CTIMessageFormatter.people_favorite_update(source, source_entry_id, enabled)

        expected = dict(set_favorite_result)
        expected.update({'class': 'people_favorite_update'})

        assert_that(result, equal_to(expected))

    def test_people_export_personal_contacts_csv_result(self):
        result = 'firstname,lastname\r\nBob,the Buidler\r\n,Alice,Wonderland\r\n'
        expected = {
            'class': 'people_export_personal_contacts_csv_result',
            'csv_contacts': result
        }

        result = CTIMessageFormatter.people_export_personal_contacts_csv_result(result)

        assert_that(result, equal_to(expected))

    def test_people_import_personal_contacts_csv_result(self):
        result = {
            'failed': [
                {
                    'line': 3,
                    'errors': ['missing fields']
                }
            ],
            'created': [
                {
                    'firstname': 'Toto',
                    'lastname': 'Bélanger'
                },
                {
                    'firstname': 'Tata',
                    'lastanem': 'Bergeron'
                }
            ]
        }
        expected = {
            'class': 'people_import_personal_contacts_csv_result',
            'failed': result['failed'],
            'created_count': len(result['created'])
        }

        result = CTIMessageFormatter.people_import_personal_contacts_csv_result(result)

        assert_that(result, equal_to(expected))

    def test_people_personal_contact_created(self):
        expected = {
            'class': 'people_personal_contact_created'
        }

        result = CTIMessageFormatter.people_personal_contact_created()

        assert_that(result, equal_to(expected))

    def test_people_personal_contact_deleted(self):
        source = 'personal'
        source_entry_id = '123456789'
        expected = {
            'class': 'people_personal_contact_deleted',
            'source': source,
            'source_entry_id': source_entry_id
        }

        result = CTIMessageFormatter.people_personal_contact_deleted(source, source_entry_id)

        assert_that(result, equal_to(expected))

    def test_people_personal_contact_raw_update(self):
        source = 'personal'
        source_entry_id = '123456789'
        expected = {
            'class': 'people_personal_contact_raw_update',
            'source': source,
            'source_entry_id': source_entry_id,
        }

        result = CTIMessageFormatter.people_personal_contact_raw_update(source, source_entry_id)

        assert_that(result, equal_to(expected))

    def test_people_personal_contact_raw_result(self):
        source = 'personal'
        source_entry_id = '123456789'
        contact_infos = {
            'firstname': 'Bob',
            'lastname': 'The Builder'
        }
        expected = {
            'class': 'people_personal_contact_raw_result',
            'source': source,
            'source_entry_id': source_entry_id,
            'contact_infos': {
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
        result = CTIMessageFormatter.user_status_update(s.xivo_uuid, s.user_uuid, s.user_id, s.status)

        assert_that(result, equal_to({
            'class': 'user_status_update',
            'data': {
                'xivo_uuid': s.xivo_uuid,
                'user_uuid': s.user_uuid,
                'user_id': s.user_id,
                'status': s.status,
            }
        }))

    def test_relations(self):
        xivo_uuid = 'my-xivo-uuid'
        user_id = '42'
        endpoint_id = '50'
        agent_id = '24'

        result = CTIMessageFormatter.relations(xivo_uuid, user_id, endpoint_id, agent_id)

        assert_that(result, equal_to({'class': 'relations',
                                      'data': {'xivo_uuid': xivo_uuid,
                                               'user_id': 42,
                                               'endpoint_id': 50,
                                               'agent_id': 24}}))

    def test_relations_no_endpoint_no_agent(self):
        xivo_uuid = 'my-xivo-uuid'
        user_id = '42'

        result = CTIMessageFormatter.relations(xivo_uuid, user_id, None, None)

        assert_that(result, equal_to({'class': 'relations',
                                      'data': {'xivo_uuid': xivo_uuid,
                                               'user_id': 42,
                                               'endpoint_id': None,
                                               'agent_id': None}}))

    def test_getlist_update_status_user(self):
        result = CTIMessageFormatter.getlist_update_status_users(s.user_id, s.status)

        assert_that(result, equal_to({
            'class': 'getlist',
            'function': 'updatestatus',
            'listname': 'users',
            'tipbxid': 'xivo',
            'tid': s.user_id,
            'status': {'availstate': s.status}
        }))

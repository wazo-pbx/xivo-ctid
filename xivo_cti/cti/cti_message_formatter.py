# -*- coding: utf-8 -*-

# Copyright (C) 2007-2016 Avencall
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

import xivo_cti


class CTIMessageFormatter(object):

    @staticmethod
    def add_queue_members(queue_member_ids):
        return {
            'class': 'getlist',
            'listname': 'queuemembers',
            'function': 'addconfig',
            'tipbxid': 'xivo',
            'list': list(queue_member_ids),
        }

    @staticmethod
    def chat(from_, to, alias, text):
        return {
            'class': 'chitchat',
            'alias': alias,
            'from': from_,
            'to': to,
            'text': text
        }

    @staticmethod
    def dial_success(exten):
        return {
            'class': 'dial_success',
            'exten': exten,
        }

    @staticmethod
    def delete_queue_members(queue_member_ids):
        return {
            'class': 'getlist',
            'listname': 'queuemembers',
            'function': 'delconfig',
            'tipbxid': 'xivo',
            'list': list(queue_member_ids),
        }

    @staticmethod
    def update_agent_status(agent_id, agent_status):
        return {'class': 'getlist',
                'listname': 'agents',
                'function': 'updatestatus',
                'tipbxid': 'xivo',
                'tid': agent_id,
                'status': agent_status}

    @staticmethod
    def update_queue_member_config(queue_member):
        return {
            'class': 'getlist',
            'listname': 'queuemembers',
            'function': 'updateconfig',
            'tipbxid': 'xivo',
            'tid': queue_member.id,
            'config': queue_member.to_cti_config(),
        }

    @staticmethod
    def ipbxcommand_error(msg):
        return {
            'class': 'ipbxcommand',
            'error_string': msg,
        }

    @staticmethod
    def login_id(session_id):
        return {'class': 'login_id',
                'sessionid': session_id,
                'xivoversion': xivo_cti.CTI_PROTOCOL_VERSION}

    @staticmethod
    def login_pass(cti_profile_id):
        return {'class': 'login_pass',
                'capalist': [cti_profile_id]}

    @staticmethod
    def people_headers_result(headers):
        return {
            'class': 'people_headers_result',
            'column_headers': headers['column_headers'],
            'column_types': headers['column_types']
        }

    @staticmethod
    def people_search_result(search_result):
        return {
            'class': 'people_search_result',
            'term': search_result['term'],
            'column_headers': search_result['column_headers'],
            'column_types': search_result['column_types'],
            'results': search_result['results'],
        }

    @staticmethod
    def people_favorites_result(favorite_result):
        return {
            'class': 'people_favorites_result',
            'column_headers': favorite_result['column_headers'],
            'column_types': favorite_result['column_types'],
            'results': favorite_result['results'],
        }

    @staticmethod
    def people_favorite_update(source, source_entry_id, enabled):
        return {
            'class': 'people_favorite_update',
            'source': source,
            'source_entry_id': source_entry_id,
            'favorite': enabled,
        }

    @staticmethod
    def phone_hintstatus_update(phone_id, status):
        return {
            'class': 'getlist',
            'listname': 'phones',
            'function': 'updatestatus',
            'tipbxid': 'xivo',
            'tid': phone_id,
            'status': {'hintstatus': status},
        }

    @staticmethod
    def agent_status_update(key, status):
        xivo_uuid, agent_id = key
        return {
            'class': 'agent_status_update',
            'data': {
                'xivo_uuid': xivo_uuid,
                'agent_id': agent_id,
                'status': status,
            }
        }

    @staticmethod
    def endpoint_status_update(key, status):
        xivo_uuid, endpoint_id = key
        return {
            'class': 'endpoint_status_update',
            'data': {
                'xivo_uuid': xivo_uuid,
                'endpoint_id': endpoint_id,
                'status': status,
            }
        }

    @staticmethod
    def user_status_update(key, status):
        xivo_uuid, user_uuid = key
        return {
            'class': 'user_status_update',
            'data': {
                'xivo_uuid': xivo_uuid,
                'user_uuid': user_uuid,
                'status': status,
            }
        }

    @staticmethod
    def people_personal_contacts_result(personal_contacts_result):
        return {
            'class': 'people_personal_contacts_result',
            'column_headers': personal_contacts_result['column_headers'],
            'column_types': personal_contacts_result['column_types'],
            'results': personal_contacts_result['results'],
        }

    @staticmethod
    def people_personal_contacts_purged():
        return {
            'class': 'people_personal_contacts_purged'
        }

    @staticmethod
    def people_personal_contact_deleted(source, source_entry_id):
        return {
            'class': 'people_personal_contact_deleted',
            'source': source,
            'source_entry_id': source_entry_id,
        }

    @staticmethod
    def people_personal_contact_created():
        return {
            'class': 'people_personal_contact_created'
        }

    @staticmethod
    def people_personal_contact_raw_update(source, source_entry_id):
        return {
            'class': 'people_personal_contact_raw_update',
            'source': source,
            'source_entry_id': source_entry_id
            }

    @staticmethod
    def people_personal_contact_raw_result(source, source_entry_id, contact_infos):
        return {
            'class': 'people_personal_contact_raw_result',
            'source': source,
            'source_entry_id': source_entry_id,
            'contact_infos': contact_infos
        }

    @staticmethod
    def people_import_personal_contacts_csv_result(result):
        return {
            'class': 'people_import_personal_contacts_csv_result',
            'failed': result.get('failed'),
            'created_count': len(result.get('created'))
        }

    @staticmethod
    def people_export_personal_contacts_csv_result(result):
        return {
            'class': 'people_export_personal_contacts_csv_result',
            'csv_contacts': result
        }

    @staticmethod
    def relations(xivo_uuid, user_id, endpoint_id, agent_id):
        user_id = int(user_id)
        endpoint_id = int(endpoint_id) if endpoint_id is not None else None
        agent_id = int(agent_id) if agent_id is not None else None

        return {'class': 'relations',
                'data': {'xivo_uuid': xivo_uuid,
                         'user_id': user_id,
                         'endpoint_id': endpoint_id,
                         'agent_id': agent_id}}

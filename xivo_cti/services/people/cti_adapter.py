# -*- coding: utf-8 -*-
# Copyright 2014-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from functools import partial
from xivo_dird_client import Client

from xivo_cti import config
from xivo_cti import dao
from xivo_cti.exception import NoSuchLineException
from xivo_cti.directory.formatter import DirectoryResultFormatter
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter

from . import old_directory_formatter

logger = logging.getLogger(__name__)


class OldProtocolCTIAdapter(object):

    _profile = '__switchboard_directory'

    def __init__(self, async_runner, cti_server):
        self._client = Client(**config['dird'])
        self._cti_server = cti_server
        self._runner = async_runner
        self._old_formatter = old_directory_formatter.OldDirectoryFormatter()

    def get_headers(self, token, user_id):
        logger.debug('Get switchboard headers')
        callback = partial(self._send_headers_result, user_id)
        self._runner.run_with_cb(callback, self._client.directories.headers,
                                 profile=self._profile, token=token)

    def _send_headers_result(self, user_id, response):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        headers = self._old_formatter.format_headers(response)
        logger.debug('Headers %s', headers)
        message = {'class': 'directory_headers',
                   'headers': headers}
        self._cti_server.send_to_cti_client(xuserid, message)

    def lookup(self, token, user_id, term):
        logger.debug('Switchboard search called for %s', term)
        callback = partial(self._send_lookup_result, user_id)
        self._runner.run_with_cb(callback, self._client.directories.lookup,
                                 profile=self._profile, term=term, token=token)

    def _send_lookup_result(self, user_id, response):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        headers, types, resultlist = self._old_formatter.format_results(response)
        switchboard_format_results = DirectoryResultFormatter.format(headers, types, resultlist)
        message = {'class': 'directory_search_result',
                   'pattern': response['term'],
                   'results': switchboard_format_results}
        self._cti_server.send_to_cti_client(xuserid, message)

    def directory_search(self, token, user_id, term, commandid):
        logger.debug('Directory search called for %s', term)
        profile = dao.user.get_context(user_id)
        callback = partial(self._send_directory_search_result, user_id, commandid)
        self._runner.run_with_cb(callback, self._client.directories.lookup,
                                 profile=profile, term=term, token=token)

    def _send_directory_search_result(self, user_id, commandid, response):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        headers, types, resultlist = self._old_formatter.format_results(response)
        message = {'class': 'directory',
                   'headers': headers,
                   'replyid': commandid,
                   'resultlist': resultlist,
                   'status': 'ok'}
        self._cti_server.send_to_cti_client(xuserid, message)


class PeopleCTIAdapter(object):

    def __init__(self, async_runner, cti_server, xivo_uuid):
        self._client = Client(**config['dird'])
        self._cti_server = cti_server
        self._runner = async_runner
        self._uuid = xivo_uuid

    def get_relations(self, user_id):
        logger.debug('User %s is requesting his relations', user_id)
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        try:
            line_id = dao.user.get_line(user_id)['id']
        except NoSuchLineException:
            line_id = None
        agent_id = dao.user.get_agent_id(user_id)

        msg = CTIMessageFormatter.relations(self._uuid, user_id, line_id, agent_id)

        self._cti_server.send_to_cti_client(xuserid, msg)

    def get_headers(self, token, user_id):
        logger.debug('Get headers called')
        profile = dao.user.get_context(user_id)
        callback = partial(self._send_headers_result, user_id)
        self._runner.run_with_cb(callback, self._client.directories.headers, profile=profile, token=token)

    def search(self, token, user_id, term):
        logger.debug('Search called')
        profile = dao.user.get_context(user_id)
        callback = partial(self._send_lookup_result, user_id)
        self._runner.run_with_cb(callback, self._client.directories.lookup, profile=profile, term=term, token=token)

    def favorites(self, token, user_id):
        logger.debug('Favorites called')
        profile = dao.user.get_context(user_id)
        callback = partial(self._send_favorites_result, user_id)
        self._runner.run_with_cb(callback, self._client.directories.favorites, profile=profile, token=token)

    def set_favorite(self, token, user_id, source, source_entry_id, enabled):
        logger.debug('Set Favorite called for user %s, contact %s/%s, favorited %s', user_id, source, source_entry_id, enabled)
        callback = partial(self._send_favorite_update, user_id, source, source_entry_id, enabled)

        if enabled:
            function = self._client.directories.new_favorite
        else:
            function = self._client.directories.remove_favorite

        self._runner.run_with_cb(callback, function, directory=source, contact=source_entry_id, token=token)

    def personal_contacts(self, token, user_id):
        logger.debug('Personal Contacts called')
        profile = dao.user.get_context(user_id)
        callback = partial(self._send_personal_contacts_result, user_id)
        self._runner.run_with_cb(callback, self._client.directories.personal, profile=profile, token=token)

    def purge_personal_contacts(self, token, user_id):
        logger.debug('Purge Personal Contacts called')
        callback = partial(self._send_personal_contacts_purged, user_id)
        self._runner.run_with_cb(callback, self._client.personal.purge, token=token)

    def personal_contact_raw(self, token, user_id, source, source_entry_id):
        logger.debug('Personal Contact called')
        callback = partial(self._send_personal_contact_raw_result, user_id, source, source_entry_id)
        self._runner.run_with_cb(callback, self._client.personal.get, contact_id=source_entry_id, token=token)

    def create_personal_contact(self, token, user_id, contact_infos):
        logger.debug('Create Personal Contact called')
        callback = partial(self._send_personal_contact_created, user_id)
        self._runner.run_with_cb(callback, self._client.personal.create, contact_infos=contact_infos, token=token)

    def delete_personal_contact(self, token, user_id, source, source_entry_id):
        logger.debug('Delete Personal Contact called')
        callback = partial(self._send_personal_contact_deleted, user_id, source, source_entry_id)
        self._runner.run_with_cb(callback, self._client.personal.delete, contact_id=source_entry_id, token=token)

    def edit_personal_contact(self, token, user_id, source, source_entry_id, contact_infos):
        logger.debug('Edit Personal Contact called')
        callback = partial(self._send_personal_contact_raw_update,
                           user_id, source, source_entry_id)
        self._runner.run_with_cb(callback, self._client.personal.edit,
                                 contact_id=source_entry_id,
                                 contact_infos=contact_infos,
                                 token=token)

    def import_personal_contacts_csv(self, token, user_id, csv_contacts):
        logger.debug('Import Personal Contacts CSV called')
        callback = partial(self._send_import_personal_contacts_csv_result, user_id)
        self._runner.run_with_cb(callback,
                                 self._client.personal.import_csv,
                                 csv_text=csv_contacts.encode('utf-8'),
                                 token=token)

    def export_personal_contacts_csv(self, token, user_id):
        logger.debug('Export Personal Contacts CSV called')
        callback = partial(self._send_export_personal_contacts_csv_result, user_id)
        self._runner.run_with_cb(callback, self._client.personal.export_csv, token=token)

    def _send_headers_result(self, user_id, headers):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_headers_result(headers)
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_lookup_result(self, user_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_search_result(result)
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_favorites_result(self, user_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_favorites_result(result)
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_favorite_update(self, user_id, source, source_entry_id, enabled, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_favorite_update(source, source_entry_id, enabled)
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_personal_contacts_result(self, user_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_personal_contacts_result(result)
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_personal_contacts_purged(self, user_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_personal_contacts_purged()
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_personal_contact_raw_result(self, user_id, source, source_entry_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_personal_contact_raw_result(source, source_entry_id, result)
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_personal_contact_created(self, user_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_personal_contact_created()
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_personal_contact_deleted(self, user_id, source, source_entry_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_personal_contact_deleted(source, source_entry_id)
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_personal_contact_raw_update(self, user_id, source, source_entry_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_personal_contact_raw_update(source, source_entry_id)
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_import_personal_contacts_csv_result(self, user_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_import_personal_contacts_csv_result(result)
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_export_personal_contacts_csv_result(self, user_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_export_personal_contacts_csv_result(result)
        self._cti_server.send_to_cti_client(xuserid, message)

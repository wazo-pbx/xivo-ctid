# Copyright (C) 2014-2015 Avencall
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

from xivo_cti.cti.cti_command import CTICommandClass


def _parse_search(msg, command):
    command.pattern = msg.get('pattern')


def _parse_set_favorite(msg, command):
    command.source = msg.get('source')
    command.source_entry_id = msg.get('source_entry_id')
    command.enabled = msg.get('favorite')


def _parse_create_personal_contact(msg, command):
    command.contact_infos = msg.get('contact_infos')


def _parse_delete_personal_contact(msg, command):
    command.source = msg.get('source')
    command.source_entry_id = msg.get('source_entry_id')


def _parse_edit_personal_contact(msg, command):
    command.source = msg.get('source')
    command.source_entry_id = msg.get('source_entry_id')
    command.contact_infos = msg.get('contact_infos')


def _parse_personal_contact_raw(msg, command):
    command.source = msg.get('source')
    command.source_entry_id = msg.get('source_entry_id')


def _parse_import_personal_contacts_csv(msg, command):
    command.csv_contacts = msg.get('csv_contacts')


PeopleSearch = CTICommandClass('people_search', match_fun=None, parse_fun=_parse_search)
PeopleSearch.add_to_registry()


PeopleHeaders = CTICommandClass('people_headers', match_fun=None, parse_fun=None)
PeopleHeaders.add_to_registry()


PeopleFavorites = CTICommandClass('people_favorites', match_fun=None, parse_fun=None)
PeopleFavorites.add_to_registry()


PeopleSetFavorite = CTICommandClass('people_set_favorite', match_fun=None, parse_fun=_parse_set_favorite)
PeopleSetFavorite.add_to_registry()


PeoplePersonalContacts = CTICommandClass('people_personal_contacts', match_fun=None, parse_fun=None)
PeoplePersonalContacts.add_to_registry()


PeoplePurgePersonalContacts = CTICommandClass('people_purge_personal_contacts', match_fun=None, parse_fun=None)
PeoplePurgePersonalContacts.add_to_registry()


PeoplePersonalContactRaw = CTICommandClass('people_personal_contact_raw', match_fun=None,
                                           parse_fun=_parse_personal_contact_raw)
PeoplePersonalContactRaw.add_to_registry()


PeopleCreatePersonalContact = CTICommandClass('people_create_personal_contact', match_fun=None,
                                              parse_fun=_parse_create_personal_contact)
PeopleCreatePersonalContact.add_to_registry()


PeopleDeletePersonalContact = CTICommandClass('people_delete_personal_contact', match_fun=None,
                                              parse_fun=_parse_delete_personal_contact)
PeopleDeletePersonalContact.add_to_registry()


PeopleEditPersonalContact = CTICommandClass('people_edit_personal_contact', match_fun=None,
                                            parse_fun=_parse_edit_personal_contact)
PeopleEditPersonalContact.add_to_registry()


PeopleExportPersonalContactsCSV = CTICommandClass('people_export_personal_contacts_csv', match_fun=None,
                                                  parse_fun=None)
PeopleExportPersonalContactsCSV.add_to_registry()


PeopleImportPersonalContactsCSV = CTICommandClass('people_import_personal_contacts_csv', match_fun=None,
                                                  parse_fun=_parse_import_personal_contacts_csv)
PeopleImportPersonalContactsCSV.add_to_registry()

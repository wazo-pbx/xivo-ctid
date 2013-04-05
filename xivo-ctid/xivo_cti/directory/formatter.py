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

import logging

from itertools import ifilter

logger = logging.getLogger(__name__)


class DirectoryFieldType:

    office = u'office'
    mobile = u'mobile'
    other = u'other'
    name = u'name'

    @classmethod
    def from_field_name(cls, field_name):
        if field_name == 'number_office':
            return cls.office
        elif field_name == 'number_mobile':
            return cls.mobile
        elif field_name == 'name':
            return cls.name
        else:
            return cls.other


class DirectoryResultFormatter(object):

    NAME_FIELD = u'name'
    NUMBER_TYPE_FIELD = u'number_type'
    NUMBER_FIELD = u'number'

    @classmethod
    def format(cls, header, types, results):
        return cls(header, types).format_results(results)

    def __init__(self, header, types):
        self._header = header
        self._types = types

    def format_results(self, results):
        if not self._is_name_available():
            logger.warning('name field type is expected for switchboard directory lookup')
            return []

        formatted_results = []
        for result in results:
            formatted_results.extend(self._format_result(result))
        return formatted_results

    def _is_name_available(self):
        print self._types
        return self.NAME_FIELD in self._types

    def _format_result(self, result):
        values = self._parse_result(result)
        title_fields = self._fields_with_title(values)
        type_fields = self._fields_with_type(values)

        formatted_results = self._combine_title_with_types(title_fields, type_fields)
        return formatted_results

    def _parse_result(self, result):
        return [value.strip() for value in result.split(';')]

    def _fields_with_title(self, values):
        title_positions = self._positions_without_type()
        fields = dict((self._header[pos], values[pos]) for pos in title_positions)
        return fields

    def _fields_with_type(self, values):
        type_positions = self._positions_with_type()

        fields = {}
        for position in type_positions:
            value = values[position]
            if value:
                fieldtype = self._types[position]
                converted_type = DirectoryFieldType.from_field_name(fieldtype)
                fields[converted_type] = value

        return fields

    def _positions_without_type(self):
        return [pos for pos, value in enumerate(self._types) if value.strip() == '']

    def _positions_with_type(self):
        return [pos for pos, value in enumerate(self._types) if value.strip() != '']

    def _combine_title_with_types(self, title_fields, type_fields):
        entries = []

        name_field = ""
        if(self.NAME_FIELD in type_fields):
            name_field = type_fields.pop(self.NAME_FIELD)

        for number_type, number in type_fields.iteritems():
            entry = dict(title_fields)
            entry[self.NAME_FIELD] = name_field
            entry[self.NUMBER_TYPE_FIELD] = number_type
            entry[self.NUMBER_FIELD] = number
            entries.append(entry)

        return entries

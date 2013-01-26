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


class DirectoryNumberType:

    office = u'office'
    mobile = u'mobile'
    other = u'other'

    @classmethod
    def from_field_name(cls, field_name):
        if field_name == 'number_office':
            return cls.office
        elif field_name == 'number_mobile':
            return cls.mobile
        else:
            return cls.other


class DirectoryResultFormatter(object):

    @classmethod
    def format(cls, headers, results):
        decomposed_results = cls._decompose_results(headers, results)
        assembled_results = cls._assemble_results(decomposed_results)
        return assembled_results

    @classmethod
    def _decompose_results(cls, headers, results):
        if 'name' not in headers:
            logger.warning('name field is expected for switchboard directory lookup')
            return []
        decomposed_results = []
        for result in results:
            values = result.split(';')
            values_trimmed = [value.strip() for value in values]
            decomposed_results.append(dict(zip(headers, values_trimmed)))
        return decomposed_results

    @classmethod
    def _assemble_results(cls, decomposed_results):
        assembled_results = []
        for decomposed_result in decomposed_results:
            cls._append_entries(assembled_results, decomposed_result)
        return assembled_results

    @classmethod
    def _append_entries(cls, assembled_results, decomposed_result):
        def field_filter(field_name):
            return field_name.startswith('number_') and decomposed_result[field_name]

        number_fields = ifilter(field_filter, decomposed_result)

        for number_field in number_fields:
            assembled_results.append(
                {
                    'name': decomposed_result['name'],
                    'number': decomposed_result[number_field],
                    'number_type': DirectoryNumberType.from_field_name(number_field),
                })

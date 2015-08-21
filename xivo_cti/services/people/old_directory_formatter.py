# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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


class OldDirectoryFormatter(object):

    _dird_only_column_types = ['favorite', 'personal']

    def format(self, dird_result):
        dird_types = dird_result['column_types']
        dird_only_column_indexes = [dird_types.index(t) for t in dird_types if t in self._dird_only_column_types]

        headers = self._filter_list(dird_result['column_headers'], dird_only_column_indexes)
        types = self._filter_list(dird_result['column_types'], dird_only_column_indexes)
        results = [self._filter_list(result['column_values'], dird_only_column_indexes)
                   for result in dird_result['results']]
        resultlist = [self._format_result(result) for result in results]

        return headers, types, resultlist

    def _format_result(self, result):
        return u';'.join([value or '' for value in result])

    def _filter_list(self, l, invalid_indexes):
        return [element for i, element in enumerate(l) if i not in invalid_indexes]

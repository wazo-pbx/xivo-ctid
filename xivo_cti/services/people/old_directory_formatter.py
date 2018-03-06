# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

logger = logging.getLogger(__name__)


class OldDirectoryFormatter(object):

    _dird_only_column_types = ['favorite', 'personal']

    def format_results(self, dird_result):
        types = dird_result['column_types']
        headers = dird_result['column_headers']
        results = dird_result['results']

        dird_only_column_indexes = self._filtered_indexes(types)

        headers = self._filter_list(headers, dird_only_column_indexes)
        types = self._filter_list(types, dird_only_column_indexes)
        results = [self._filter_list(result['column_values'], dird_only_column_indexes)
                   for result in results]

        resultlist = [self._format_result(result) for result in results]

        return headers, types, resultlist

    def format_headers(self, dird_result):
        logger.debug('Formatting headers %s', dird_result)
        types = dird_result['column_types']
        headers = dird_result['column_headers']

        extra_number_col_indexes = [types.index(t) for t in types if t.startswith('number_')][1:]
        types_with_one_number = self._filter_list(types, extra_number_col_indexes)
        headers_with_one_number = self._filter_list(headers, extra_number_col_indexes)

        dird_only_column_indexes = self._filtered_indexes(types_with_one_number)

        cleaned_up_types = ['number' if t.startswith('number') else t for t in types_with_one_number]

        return zip(self._filter_list(headers_with_one_number, dird_only_column_indexes),
                   self._filter_list(cleaned_up_types, dird_only_column_indexes))

    def _filtered_indexes(self, types):
        return [types.index(t) for t in types if t in self._dird_only_column_types]

    def _format_result(self, result):
        return u';'.join(value or '' for value in result)

    def _filter_list(self, l, invalid_indexes):
        return [element for i, element in enumerate(l) if i not in invalid_indexes]

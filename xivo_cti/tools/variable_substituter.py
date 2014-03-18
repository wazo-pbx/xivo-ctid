# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

import base64
import contextlib
import logging
import re
import urllib2

logger = logging.getLogger('sheet')

USER_PICTURE_URL = 'http://127.0.0.1/getatt.php?id=%s&obj=user'


def substitute_with_default(string_containing_variables,
                            default_string,
                            variable_values):
    substituter = _Substituer(variable_values)
    return substituter.substitute_with_default(default_string, string_containing_variables)


def substitute(string_containing_variables, variable_values):
    substituter = _Substituer(variable_values)
    return substituter.substitute(string_containing_variables)


class _Substituer(object):

    _VARIABLE_NAME_REGEX = re.compile(r'\{([^}]+)\}')

    def __init__(self, variables):
        self._nb_substitutions = 0
        self._nb_failed_substitutions = 0
        self.variables = variables

    def substitute_with_default(self, default_value, display_value):
        substitution_result = self._VARIABLE_NAME_REGEX.sub(self._regex_callback, display_value)
        if self._nb_substitutions == 0:
            return display_value
        elif self._nb_failed_substitutions == self._nb_substitutions:
            return default_value if default_value else display_value
        else:
            return substitution_result

    def substitute(self, display_value):
        return self._VARIABLE_NAME_REGEX.sub(self._regex_callback, display_value)

    def _regex_callback(self, m):
        variable_name = m.group(1)
        variable_value = self._replace_variable(variable_name)
        self._nb_substitutions += 1
        if variable_value is None:
            self._nb_failed_substitutions += 1
            return m.group(0)
        else:
            if not isinstance(variable_value, basestring):
                variable_value = str(variable_value)
            return variable_value

    def _get_user_picture(self, user_id):
        url = USER_PICTURE_URL % user_id
        try:
            with contextlib.closing(urllib2.urlopen(url)) as picture_file:
                picture_data = picture_file.read()
            return base64.b64encode(picture_data)
        except urllib2.HTTPError:
            logger.warning('Could not load picture from %s', url)

    def _replace_variable(self, variable_name):
        if variable_name == 'xivo-callerpicture' and 'xivo-userid' in self.variables:
            user_id = self.variables['xivo-userid']
            return self._get_user_picture(user_id)

        if variable_name in self.variables:
            return self.variables[variable_name]

        logger.warning('Could not replace variable %r', variable_name)
        return None

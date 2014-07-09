# Copyright (C) 2014 Avencall
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

PeopleSearch = CTICommandClass('people_search', match_fun=None, parse_fun=_parse_search)
PeopleSearch.add_to_registry()


PeopleHeaders = CTICommandClass('people_headers', match_fun=None, parse_fun=None)
PeopleHeaders.add_to_registry()

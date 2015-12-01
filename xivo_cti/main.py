# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
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

import sys
import xivo_dao

from xivo_cti import config
from xivo_cti import cti_config
from xivo_cti.ioc.context import context
from xivo_cti.ioc import register_class


def main():
    cti_config.init_cli_config(sys.argv[1:])
    cti_config.init_config_file()
    cti_config.init_auth_config()
    xivo_dao.init_db_from_config(config)
    cti_config.update_db_config()

    register_class.setup()

    ctid = context.get('cti_server')
    ctid.setup()
    ctid.run()


if __name__ == '__main__':
    main()

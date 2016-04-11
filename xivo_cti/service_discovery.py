# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
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

import requests

from socket import socket, error as socket_error

from xivo_cti.http_app import HTTPInterface


# this function is not executed from the main thread
def self_check(config):
    host = 'localhost'
    http_port = config['rest_api']['http']['port']
    cti_port = config['client']['port']
    info_url = 'http://{}:{}/{}/infos'.format(host, http_port, HTTPInterface.VERSION)

    try:
        http_up = requests.get(info_url).status_code == 200
    except Exception:
        return False

    s = socket()
    try:
        s.connect((host, cti_port))
        cti_up = True
    except socket_error:
        return False
    finally:
        s.close()

    return http_up and cti_up

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

import os
import logging
import time
import threading

from cherrypy import wsgiserver
from flask import Flask
from flask.ext import restful
from flask_cors import CORS
from werkzeug.contrib.fixers import ProxyFix

logger = logging.getLogger(__name__)


class Endpoints(restful.Resource):

    def get(self, endpoint_id):
        uuid = self.main_thread_proxy.get_uuid()
        endpoint_status = self.main_thread_proxy.get_endpoint_status(str(endpoint_id))

        try:
            return {
                'id': endpoint_id,
                'origin_uuid': uuid.get(),
                'status': int(endpoint_status.get()),
            }
        except LookupError as e:
            return {'reason': [str(e)],
                    'timestamp': [time.time()],
                    'status_code': 404}, 404


class Users(restful.Resource):

    def get(self, user_id):
        uuid = self.main_thread_proxy.get_uuid()
        user_presence = self.main_thread_proxy.get_user_presence(str(user_id))

        try:
            return {
                'id': user_id,
                'origin_uuid': uuid.get(),
                'presence': user_presence.get(),
            }
        except LookupError as e:
            return {'reason': [str(e)],
                    'timestamp': [time.time()],
                    'status_code': 404}, 404


class Infos(restful.Resource):

    def get(self):
        uuid = self.main_thread_proxy.get_uuid()

        return {
            'uuid': uuid.get(),
        }


class HTTPInterface(object):

    VERSION = '0.1'

    _resources = [
        (Endpoints, '/endpoints/<int:endpoint_id>'),
        (Infos, '/infos'),
        (Users, '/users/<int:user_id>'),
    ]

    def __init__(self, config, main_thread_proxy):
        app = Flask('xivo_ctid')
        app.wsgi_app = ProxyFix(app.wsgi_app)
        app.secret_key = os.urandom(24)
        self.load_cors(app, config)
        api = restful.Api(app, prefix='/{}'.format(self.VERSION))
        self._add_resources(api, main_thread_proxy)
        bind_addr = (config['listen'], config['port'])
        wsgi_app = wsgiserver.WSGIPathInfoDispatcher({'/': app})
        self._server = wsgiserver.CherryPyWSGIServer(bind_addr=bind_addr,
                                                     wsgi_app=wsgi_app)

    def load_cors(self, app, config):
        cors_config = dict(config.get('cors', {}))
        enabled = cors_config.pop('enabled', False)
        if enabled:
            CORS(app, **cors_config)

    def start(self):
        self._thread = threading.Thread(target=self._start_async)
        self._thread.daemon = True
        self._thread.name = 'HTTPServerThread'
        self._thread.start()

    def _add_resources(self, api, main_thread_proxy):
        for Resource, url in self._resources:
            Resource.main_thread_proxy = main_thread_proxy
            api.add_resource(Resource, url)

    def _start_async(self):
        try:
            self._server.start()
        finally:
            self._server.stop()

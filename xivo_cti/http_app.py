# -*- coding: utf-8 -*-

# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
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

from cheroot import wsgi
from flask import Flask
from flask_cors import CORS
from flask_restful import Api, Resource
from xivo import http_helpers

from xivo_cti import CTI_PROTOCOL_VERSION
from xivo_cti.swagger.resource import SwaggerResource

logger = logging.getLogger(__name__)


class Endpoints(Resource):

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


class Users(Resource):

    def get(self, user_id):
        origin_uuid = self.main_thread_proxy.get_uuid()
        user = self.main_thread_proxy.get_user(user_id)
        user_presence = self.main_thread_proxy.get_user_presence(str(user_id))

        try:
            user = user.get()
            id_ = user['id']
            uuid = user['uuid']

            return {
                'id': id_,
                'user_uuid': uuid,
                'origin_uuid': origin_uuid.get(),
                'presence': user_presence.get(),
            }
        except LookupError as e:
            return {'reason': [str(e)],
                    'timestamp': [time.time()],
                    'status_code': 404}, 404


class Infos(Resource):

    def get(self):
        uuid = self.main_thread_proxy.get_uuid()

        return {
            'uuid': uuid.get(),
            'cti_protocol_version': CTI_PROTOCOL_VERSION,
        }


class HTTPInterface(object):

    VERSION = '0.1'

    _resources = [
        (Endpoints, '/endpoints/<int:endpoint_id>'),
        (Infos, '/infos'),
        (Users, '/users/<user_id>'),
        (SwaggerResource, SwaggerResource.api_path),
    ]

    def __init__(self, config, main_thread_proxy):
        app = Flask('xivo_ctid')
        http_helpers.add_logger(app, logger)
        app.after_request(http_helpers.log_request)
        app.secret_key = os.urandom(24)
        self.load_cors(app, config)
        api = Api(app, prefix='/{}'.format(self.VERSION))
        self._add_resources(api, main_thread_proxy)
        bind_addr = (config['http']['listen'], config['http']['port'])
        wsgi_app = wsgi.WSGIPathInfoDispatcher({'/': app})
        self._server = wsgi.WSGIServer(bind_addr=bind_addr,
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
        for resource, url in self._resources:
            resource.main_thread_proxy = main_thread_proxy
            api.add_resource(resource, url)

    def _start_async(self):
        try:
            self._server.start()
        finally:
            self._server.stop()

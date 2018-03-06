# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+


from flask import Flask, make_response

app = Flask(__name__)


@app.route('/0.1/api/api.yml', methods=['GET'])
def get_api():
    with open('/tmp/api.yml', 'r') as api_spec:
        return make_response(api_spec.read()), 200, {'Content-Type': 'application/x-yaml'}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9495)

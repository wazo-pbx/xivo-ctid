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


from flask import Flask, make_response

app = Flask(__name__)


@app.route('/0.1/api/api.json', methods=['GET'])
def get_api():
    with open('/tmp/api.json', 'r') as api_spec:
        return make_response(api_spec.read()), 200, {'Content-Type': 'application/json'}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9495)

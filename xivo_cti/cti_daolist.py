# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
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

import logging

from xivo_dao.helpers.db_utils import session_scope

from xivo_dao import (group_dao, agent_dao,
                      meetme_dao, queue_dao, voicemail_dao,
                      user_dao, trunk_dao, user_line_dao)

logger = logging.getLogger('daolist')


class UnknownListName(Exception):
    pass


class NotFoundError(Exception):
    pass


class DaoList(object):

    def __init__(self, listname):
        self.listname = listname

    def get(self, id):
        method_suffix = self.listname[:-1]
        method = self._get_method(method_suffix)
        try:
            return method(id)
        except KeyError:
            raise
        except LookupError:
            raise NotFoundError(self.listname, id)

    def get_list(self):
        method_suffix = self.listname
        method = self._get_method(method_suffix)
        return method()

    def _get_method(self, method_suffix):
        name = '_get_%s' % method_suffix
        try:
            return getattr(self, name)
        except AttributeError:
            raise UnknownListName(self.listname)

    def _get_users(self):
        with session_scope():
            return user_dao.get_users_config()

    def _get_user(self, user_id):
        with session_scope():
            return user_dao.get_user_config(user_id)

    def _get_phones(self):
        with session_scope():
            full_line = []
            full_line.extend(user_line_dao.all_with_protocol('sip'))
            full_line.extend(user_line_dao.all_with_protocol('iax'))
            full_line.extend(user_line_dao.all_with_protocol('sccp'))
            full_line.extend(user_line_dao.all_with_protocol('custom'))

            res = {}
            for line in full_line:
                line, protocol, user = line
                res.update(self._format_line_data(line, protocol, user))
            return res

    def _get_phone(self, id):
        with session_scope():
            line, protocol, user = user_line_dao.get_with_line_id(id)
            return self._format_line_data(line, protocol, user)

    def _format_line_data(self, line, protocol, user):
        res = {}
        merged_line = protocol.todict()
        merged_line.update(line.todict())
        merged_line['iduserfeatures'] = user.id
        merged_line['useridentity'] = '%s %s' % (user.firstname, user.lastname)
        protocol = merged_line['protocol'].upper()
        iface_name = merged_line['name']
        merged_line['identity'] = '%s/%s' % (protocol, iface_name)
        res[str(line.id)] = merged_line
        return res

    def _get_groups(self):
        with session_scope():
            res = {}
            groups = group_dao.all()
            for group in groups:
                res.update(self._format_group_data(group))
            return res

    def _get_group(self, id):
        with session_scope():
            group = group_dao.get(id)
            return self._format_group_data(group)

    def _format_group_data(self, group):
        res = {}
        key = str(group.id)
        res[key] = group.todict()
        res[key]['fullname'] = '%s (%s)' % (group.name, group.context)
        return res

    def _get_agents(self):
        with session_scope():
            res = {}
            agents = agent_dao.all()
            for agent in agents:
                res.update(self._format_agent_data(agent))
            return res

    def _get_agent(self, id):
        with session_scope():
            agent = agent_dao.get(id)
            return self._format_agent_data(agent)

    def _format_agent_data(self, agent):
        res = {}
        key = str(agent.id)
        res[key] = agent.todict()
        return res

    def _get_meetmes(self):
        with session_scope():
            res = {}
            meetmes = meetme_dao.all()
            for meetme in meetmes:
                res.update(self._format_meetme_data(meetme))
            return res

    def _get_meetme(self, id):
        with session_scope():
            meetme = meetme_dao.get(id)
            return self._format_meetme_data(meetme)

    def _format_meetme_data(self, meetme):
        res = {}
        key = str(meetme.id)
        res[key] = meetme.todict()
        return res

    def _get_queues(self):
        with session_scope():
            res = {}
            queues = queue_dao.all_queues()
            for queue in queues:
                res.update(self._format_queue_data(queue))
            return res

    def _get_queue(self, id):
        with session_scope():
            queue = queue_dao.get(id)
            return self._format_queue_data(queue)

    def _format_queue_data(self, queue):
        res = {}
        key = str(queue.id)
        res[key] = queue.todict()
        res[key]['identity'] = '%s (%s@%s)' % (queue.displayname, queue.number, queue.context)
        return res

    def _get_voicemails(self):
        with session_scope():
            res = {}
            voicemails = voicemail_dao.all()
            for voicemail in voicemails:
                res.update(self._format_voicemail_data(voicemail))
            return res

    def _get_voicemail(self, id):
        with session_scope():
            voicemail = voicemail_dao.get(id)
            return self._format_voicemail_data(voicemail)

    def _format_voicemail_data(self, voicemail):
        with session_scope():
            res = {}
            key = str(voicemail.uniqueid)
            res[key] = voicemail.todict()
            res[key]['fullmailbox'] = '%s@%s' % (voicemail.mailbox, voicemail.context)
            res[key]['identity'] = '%s (%s@%s)' % (voicemail.fullname, voicemail.mailbox, voicemail.context)
            return res

    def _get_trunks(self):
        with session_scope():
            res = {}
            trunks = trunk_dao.all()
            for trunk in trunks:
                res.update(self._format_trunk_data(trunk))
            return res

    def _get_trunk(self, id):
        with session_scope():
            trunk = trunk_dao.get(id)
            return self._format_trunk_data(trunk)

    def _format_trunk_data(self, trunk):
        res = {}
        key = str(trunk.id)
        res[key] = trunk.todict()
        return res

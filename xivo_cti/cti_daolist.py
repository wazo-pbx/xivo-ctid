# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_dao.helpers.db_utils import session_scope

from xivo_dao import agent_dao, meetme_dao, queue_dao, voicemail_dao, user_line_dao

from xivo_cti.database import user_db


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
            return user_db.get_users_config()

    def _get_user(self, user_id):
        with session_scope():
            return user_db.get_user_config(user_id)

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
        res = {}
        key = str(voicemail.uniqueid)
        res[key] = voicemail.todict()
        res[key]['fullmailbox'] = '%s@%s' % (voicemail.mailbox, voicemail.context)
        res[key]['identity'] = '%s (%s@%s)' % (voicemail.fullname, voicemail.mailbox, voicemail.context)
        return res

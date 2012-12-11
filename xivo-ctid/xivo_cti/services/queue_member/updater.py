# -*- coding: UTF-8 -*-

import logging
from xivo_cti.services.queue_member.member import QueueMember, QueueMemberState
from xivo_dao import queue_member_dao
from xivo_cti.services.queue_member.common import format_queue_member_id

logger = logging.getLogger('QueueMemberUpdater')


class QueueMemberUpdater(object):

    def __init__(self, queue_member_manager):
        self._queue_member_manager = queue_member_manager

    def on_initialization(self):
        logger.debug('on initialization')
        self._add_dao_queue_members_to_manager()
        # we also need to
        # * request QueueStatus of all asterisk queue members
        # * request AgentStatus of all agents
        # but this is actually not done in this class
        # TODO créer une commande "AMIAgentStatus" dans xivo-agent

    def _add_dao_queue_members_to_manager(self):
        for dao_queue_member in queue_member_dao.get_queue_members_for_queues():
            queue_name = dao_queue_member.queue_name
            member_name = dao_queue_member.member_name
            state = QueueMemberState.from_dao_queue_member(dao_queue_member)
            queue_member = QueueMember(queue_name, member_name, state)
            self._queue_member_manager._add_queue_member(queue_member)

    def on_ami_agent_logoff(self, ami_event):
        logger.debug('on ami agent logoff')
        agent_number = ami_event['AgentNumber']
        self._update_agent_queue_members_as_not_logged(agent_number)

    def on_ami_agent_status(self, ami_event):
        logger.debug('on ami agent status')
        # XXX l'evenement n'existe pas encore dans xivo-agent
        # XXX techniquement on n'a pas besoin de cet evenemnt si, a l'initialisation,
        #     pour les agents, au lieu de dire status "UNKNOWN" on met status "unlogged".
        #     Par contre c'est p-e un petit peu plus "robuste" que de faire ca
        agent_number = ami_event['AgentNumber']
        logged = bool(int(ami_event['Logged']))
        if not logged:
            self._update_agent_queue_members_as_not_logged(agent_number)

    def _update_agent_queue_members_as_not_logged(self, agent_number):
        for queue_member in self._queue_member_manager.get_queue_members_by_agent_number(agent_number):
            old_state = queue_member.state
            new_state = old_state.copy()
            new_state.status = QueueMemberState.STATUS_NOT_LOGGED
            new_state.paused = False
            self._queue_member_manager._update_queue_member(queue_member, new_state)

    def on_ami_queue_member(self, ami_event):
        logger.debug('on ami queue member')
        queue_name = ami_event['Queue']
        member_name = ami_event['Name']

        # XXX some duplication
        queue_member = self._queue_member_manager.get_queue_member_by_name(queue_name, member_name)
        if queue_member is None:
            # probably a member of a group
            queue_member_id = format_queue_member_id(queue_name, member_name)
            logger.info('ignoring queue member event for %r: unknown member', queue_member_id)
        else:
            new_state = QueueMemberState.from_ami_queue_member(ami_event)
            self._queue_member_manager._update_queue_member(queue_member, new_state)

    def on_ami_queue_member_status(self, ami_event):
        logger.debug('on ami queue member status')
        queue_name = ami_event['Queue']
        member_name = ami_event['MemberName']

        # XXX some duplication
        queue_member = self._queue_member_manager.get_queue_member_by_name(queue_name, member_name)
        if queue_member is None:
            # probably a member of a group
            queue_member_id = format_queue_member_id(queue_name, member_name)
            logger.info('ignoring queue member status event for %r: unknown member', queue_member_id)
        else:
            new_state = QueueMemberState.from_ami_queue_member_status(ami_event)
            self._queue_member_manager._update_queue_member(queue_member, new_state)

    def on_ami_queue_member_added(self, ami_event):
        logger.debug('on ami queue member added')
        queue_name = ami_event['Queue']
        member_name = ami_event['MemberName']
        queue_member = self._queue_member_manager.get_queue_member_by_name(queue_name, member_name)
        if queue_member is None:
            queue_member_id = format_queue_member_id(queue_name, member_name)
            logger.info('ignoring queue member added event for %r: unknown member', queue_member_id)
        else:
            if not queue_member.is_agent():
                logger.info('ignoring queue member added event for %r: not an agent', queue_member.id)
            else:
                new_state = QueueMemberState.from_ami_queue_member_added(ami_event)
                self._queue_member_manager._update_queue_member(queue_member, new_state)

    def on_ami_queue_member_removed(self, ami_event):
        logger.debug('on ami queue member removed')
        queue_name = ami_event['Queue']
        member_name = ami_event['MemberName']
        queue_member = self._queue_member_manager.get_queue_member_by_name(queue_name, member_name)
        if queue_member is None:
            queue_member_id = format_queue_member_id(queue_name, member_name)
            logger.info('ignoring queue member removed event for %r: unknown member', queue_member_id)
        else:
            if not queue_member.is_agent():
                logger.info('ignoring queue member removed event for %r: not an agent', queue_member.id)
            else:
                new_state = queue_member.state.copy()
                new_state.status = QueueMemberState.STATUS_NOT_LOGGED
                new_state.paused = False
                self._queue_member_manager._update_queue_member(queue_member, new_state)

    def on_ami_queue_member_paused(self, ami_event):
        logger.debug('on ami queue member paused')
        queue_name = ami_event['Queue']
        member_name = ami_event['MemberName']
        queue_member = self._queue_member_manager.get_queue_member_by_name(queue_name, member_name)
        if queue_member is None:
            queue_member_id = format_queue_member_id(queue_name, member_name)
            logger.info('ignoring queue member paused event for %r: unknown member', queue_member_id)
        else:
            paused = bool(int(ami_event['Paused']))
            new_state = queue_member.state.copy()
            new_state.paused = paused
            self._queue_member_manager._update_queue_member(queue_member, new_state)

    def on_ami_queue_member_penalty(self, ami_event):
        logger.debug('on ami queue member penalty')
        # XXX est-ce que c'est vraiment necessaire ou est-ce qu'on ne va pas déjà recevoir
        #     un QueueMemberStatus ?
        pass

    def on_webi_update(self):
        # 1. on obtient la liste des queuemembers dans la base (seulement des files, pas des groupes)
        # 2. on obtient la liste des queuemembers dans le manager
        # 3.1 tous ceux qui ont été ajouter, alors on les rajoutent avec l'état par default
        #     en fonction de si c'est un agent ou non et on demande son status via l'AMI
        # 3.2 tous ceux qui ont été enlever, on les enleve
        pass

    def register_ami_events(self, ami_handler):
        ami_handler.register_userevent_callback('AgentLogoff', self.on_ami_agent_logoff)
        ami_handler.register_userevent_callback('AgentStatus', self.on_ami_agent_status)
        ami_handler.register_callback('QueueMember', self.on_ami_queue_member)
        ami_handler.register_callback('QueueMemberStatus', self.on_ami_queue_member_status)
        ami_handler.register_callback('QueueMemberAdded', self.on_ami_queue_member_added)
        ami_handler.register_callback('QueueMemberRemoved', self.on_ami_queue_member_removed)
        ami_handler.register_callback('QueueMemberPaused', self.on_ami_queue_member_paused)
        ami_handler.register_callback('QueueMemberPenalty', self.on_ami_queue_member_penalty)

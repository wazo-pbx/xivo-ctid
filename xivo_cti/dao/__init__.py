# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.dao.agent_dao import AgentDAO
from xivo_cti.dao.channel_dao import ChannelDAO
from xivo_cti.dao.forward_dao import ForwardDAO
from xivo_cti.dao.queue_dao import QueueDAO
from xivo_cti.dao.meetme_dao import MeetmeDAO
from xivo_cti.dao.phone_dao import PhoneDAO
from xivo_cti.dao.user_dao import UserDAO
from xivo_cti.dao.voicemail_dao import VoicemailDAO
from xivo_cti.dao.innerdata_dao import InnerdataDAO
from xivo_cti.ioc.context import context

from xivo_dao.resources.func_key import dao as func_key_dao

agent = None
channel = None
queue = None
meetme = None
phone = None
user = None
voicemail = None
innerdata = None
forward = None


def instanciate_dao(innerdata_obj, queue_member_manager):
    global agent
    agent = AgentDAO(innerdata_obj, queue_member_manager)
    global channel
    channel = ChannelDAO(innerdata_obj, context.get('call_form_variable_aggregator'))
    global queue
    queue = QueueDAO(innerdata_obj)
    global meetme
    meetme = MeetmeDAO(innerdata_obj)
    global phone
    phone = PhoneDAO(innerdata_obj)
    global user
    user = UserDAO(innerdata_obj)
    global voicemail
    voicemail = VoicemailDAO(innerdata_obj)
    global innerdata
    innerdata = InnerdataDAO(innerdata_obj)
    global forward
    forward = ForwardDAO(func_key_dao)

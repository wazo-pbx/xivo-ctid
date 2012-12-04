# XiVO CTI Server

from xivo_cti.dao.agent_dao import AgentDAO
from xivo_cti.dao.channel_dao import ChannelDAO
from xivo_cti.dao.queue_member_dao import QueueMemberDAO

agent = None
queue_member = None
channel = None


def instanciate_dao(innerdata):
    global queue_member
    queue_member = QueueMemberDAO(innerdata)
    global channel
    channel = ChannelDAO(innerdata)
    global agent
    agent = AgentDAO(innerdata, queue_member)

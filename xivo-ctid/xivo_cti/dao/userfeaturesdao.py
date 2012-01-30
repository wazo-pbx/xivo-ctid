from xivo_cti.dao.alchemy.userfeatures import UserFeatures
from xivo_cti.dao.alchemy import dbconnection


class UserFeaturesDAO(object):

    def __init__(self, session):
        self._session = session

    def enable_dnd(self, user_id):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablednd': 1})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['enablednd'] = True

    @classmethod
    def new_from_uri(cls, uri):
        connection = dbconnection.get_connection(uri)
        return cls(connection.get_session())

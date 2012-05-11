# -*- coding: utf-8 -*-


class PresenceServiceManager(object):
    def is_valid_presence(self, profile, presence):
        presences = self.innerdata_dao.get_presences(profile)
        return presence in presences

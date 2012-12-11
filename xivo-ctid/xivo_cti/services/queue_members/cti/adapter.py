# -*- coding: UTF-8 -*-

# XXX s'occupe de recevoir les commandes des clients CTI, faire la requete
#     au manager et retourner la response


class QueueMemberCTIAdapter(object):

    def __init__(self, queue_member_manager):
        self._queue_member_manager = queue_member_manager

    def get_list(self):
        # XXX appeler a partir de innerdata
        return self._queue_member_manager.get_queue_members_id()

    def get_config(self, queue_member_id):
        # XXX appeler a partir de innerdata
        # retourne un dictionaire vide si queue_member_id n'existe pas
        queue_member = self._queue_member_manager.get_queue_member(queue_member_id)
        if queue_member is None:
            return {}
        else:
            return queue_member.to_cti_config()

    def get_status(self, queue_member_id):
        # XXX appeler a partir de innerdata
        # retourne null si queue_member_id n'existe pas
        queue_member = self._queue_member_manager.get_queue_member(queue_member_id)
        if queue_member is None:
            return None
        else:
            return queue_member.to_cti_status()

import logging
from xivo_cti.client_connection import ClientConnection

logger = logging.getLogger("StatisticsNotifier")

class StatisticsNotifier(object):

    COMMAND_CLASS = 'getqueuesstats'
    CONTENT = 'stats'

    def __init__(self):
        self.statistic = None
        self.cti_connections = set()
        self.closed_cti_connections = set()

    def on_stat_changed(self, statistic):
        logger.info(statistic)
        self.statistic = statistic
        for cti_connection in self.cti_connections:
            self._send_statistic(cti_connection)

        for closed_connection in self.closed_cti_connections:
            self.cti_connections.remove(closed_connection)
        self.closed_cti_connections.clear()

    def subscribe(self, cti_connection):
        logger.info('xivo client subscribing ')

        if self.statistic is not None:
            cti_connection.send_message({'class':self.COMMAND_CLASS,
                                     self.CONTENT : self.statistic
                                    })

        self.cti_connections.add(cti_connection)

    def _send_statistic(self, cti_connection):
        try:
            cti_connection.send_message({'class':self.COMMAND_CLASS,
                                     self.CONTENT : self.statistic
                                    })
        except ClientConnection.CloseException:
            self.closed_cti_connections.add(cti_connection)

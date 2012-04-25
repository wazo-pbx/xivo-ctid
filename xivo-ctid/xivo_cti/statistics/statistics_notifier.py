import logging

logger = logging.getLogger("StatisticsNotifier")

class StatisticsNotifier(object):

    def __init__(self):
        pass

    def on_stat_changed(self, statistic):
        logger.info(statistic)

#!/usr/bin/env python

from distutils.core import setup

setup(
    name='xivo-ctid',
    version='1.2',
    description='XiVO CTI Server Daemon',
    author='Avencall',
    author_email='xivo-dev@lists.proformatique.com',
    url='http://wiki.xivo.fr/',
    packages=['xivo_cti',
              'xivo_cti.model',
              'xivo_cti.alarm',
              'xivo_cti.lists',
              'xivo_cti.statistics',
              'xivo_cti.dao',
              'xivo_cti.dao.alchemy',],
    scripts=['bin/xivo-ctid'],
)

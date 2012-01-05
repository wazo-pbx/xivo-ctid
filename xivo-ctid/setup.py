#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
              'xivo_cti.ami',
              'xivo_cti.lists',
              'xivo_cti.statistics',
              'xivo_cti.dao',
              'xivo_cti.dao.alchemy',
              'xivo_cti.cti',
              'xivo_cti.cti.commands'],
    scripts=['bin/xivo-ctid'],
    data_files=[('/etc/pf-xivo/xivo-ctid', ['etc/allowedxlets.json',
                                            'etc/default_config.json'])],
)

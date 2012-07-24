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
              'xivo_cti.ami',
              'xivo_cti.ami.actions',
              'xivo_cti.lists',
              'xivo_cti.interfaces',
              'xivo_cti.statistics',
              'xivo_cti.dao',
              'xivo_cti.cti',
              'xivo_cti.cti.commands',
              'xivo_cti.cti.commands.getlists',
              'xivo_cti.cti.commands.user_service',
              'xivo_cti.directory',
              'xivo_cti.directory.data_sources',
              'xivo_cti.services',
              'xivo_cti.services.meetme',
              'xivo_cti.funckey',
              'xivo_cti.tools'],
    scripts=['bin/xivo-ctid'],
    data_files=[('/etc/pf-xivo/xivo-ctid', ['etc/allowedxlets.json',
                                            'etc/default_config.json'])],
)

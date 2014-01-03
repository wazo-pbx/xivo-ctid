#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fnmatch
import os

from distutils.core import setup

packages = [
    package for package, _, _ in os.walk('xivo_cti')
    if not fnmatch.fnmatch(package, '*tests')
]

setup(
    name='xivo-ctid',
    version='1.2',
    description='XiVO CTI Server Daemon',
    author='Avencall',
    author_email='xivo-dev@lists.proformatique.com',
    url='http://wiki.xivo.fr/',
    packages=packages,
    scripts=['bin/xivo-ctid'],
)

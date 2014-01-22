#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fnmatch
import os

from distutils.core import setup


def is_package(path):
    is_svn_dir = fnmatch.fnmatch(path, '*/.svn*')
    is_test_module = fnmatch.fnmatch(path, '*tests')
    return not (is_svn_dir or is_test_module)

packages = [p for p, _, _ in os.walk('xivo_cti') if is_package(p)]

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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2014-2015 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+


from setuptools import setup
from setuptools import find_packages


setup(
    name='xivo-ctid',
    version='1.2',
    description='XiVO CTI Server Daemon',
    author='Wazo Authors',
    author_email='dev.wazo@gmail.com',
    url='http://wazo.community',
    packages=find_packages(),
    package_data={
        'xivo_cti.swagger': ['*.yml'],
    },
    scripts=['bin/ami-proxy', 'bin/xivo-ctid'],
)

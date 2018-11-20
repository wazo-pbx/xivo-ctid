# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import os

from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase


class BaseIntegrationTest(AssetLaunchingTestCase):

    assets_root = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
    service = 'ctid'

# -*- coding: utf-8 -*-
# Copyright © 2023-present Worldr Technologies Limited. All Rights Reserved.
"""Nhound."""
from importlib import metadata

import pendulum

__version__ = metadata.version(__package__)

del metadata  # optional, avoids polluting the results of dir(__package__)

NOW = pendulum.now("UTC")  # We should have a basic timer of now.

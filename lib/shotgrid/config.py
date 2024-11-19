#!/bin/env/python

__doc__ = """
Contains default configuration settings.
"""

import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
SG_SCRIPT_URL = os.getenv("SG_SCRIPT_URL")
SG_SCRIPT_NAME = os.getenv("SG_SCRIPT_NAME")
SG_SCRIPT_KEY = os.getenv("SG_SCRIPT_KEY")

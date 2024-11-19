#!/usr/bin/env python

__doc__ = """
Contains logger setup.
"""

import logging

from shotgrid import config

log = logging.Logger("shotgrid")
log.setLevel(config.LOG_LEVEL)

streamHandler = logging.StreamHandler()
streamHandler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
log.addHandler(streamHandler)

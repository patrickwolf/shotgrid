#!/bin/env/python

__doc__ = """
Shotgrid Python API wrapper.
"""

__prog__ = "shotgrid"
__version__ = "0.2.0"
__author__ = "ryan@rsg.io"

import envstack

envstack.init(__prog__)

from .shotgrid import Shotgrid

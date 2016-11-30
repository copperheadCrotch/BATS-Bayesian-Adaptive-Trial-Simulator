"""
A fast python module with friendly GUI for Bayesian Multi-Arm Multi-Stage Design
"""
import sys as _sys
import os as _os

_sys.path.append(_os.path.abspath('../'))

__version__ = '1.0.0b8'
__author__ = 'Zhenning Yu'
__email__ = 'yuzhenning.bio@gmail.com'
__All__=['__init__']

from .BATS import __init__

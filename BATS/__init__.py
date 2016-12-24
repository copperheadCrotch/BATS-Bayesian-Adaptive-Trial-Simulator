"""
A fast python module with friendly GUI for Bayesian Multi-Arm Multi-Stage Design
"""
import sys as _sys
import os as _os

_sys.path.append(_os.path.abspath('../'))

__version__ = '1.1.0a4'
__author__ = 'Zhenning Yu'
__email__ = 'yuzhenning.bio@gmail.com'
__All__=['main', 'FixedTrial', 'CalPosteriorProbability']

from .BATS import main
from .BATS import FixedTrial
from .BATS import CalPosteriorProbability

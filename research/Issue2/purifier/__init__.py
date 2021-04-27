# -*- coding: utf-8 -*-

#
# check python version
#
import sys
from .text_extractor import TEAgent

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

__all__ = ['TEAgent']

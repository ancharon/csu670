#!/usr/bin/env python
# encoding: utf-8
"""
theseus.py

Copyright (c) 2008 Nathan Palmer, Ethan Caldwell, Dave Fier. All rights reserved.
"""

import sys,os
from xml import sax
import unittest
import gameparser
from gameplayer import GamePlayer


class main:
    def __init__(self):
        pass

if __name__ == '__main__':
    myGameplayer = GamePlayer()
    myGameplayer.takeTurns()
    

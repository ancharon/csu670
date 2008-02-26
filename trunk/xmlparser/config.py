#!/usr/bin/env python
# encoding: utf-8
"""
config.py
This file is meant to hold global variables for use throughout the program.

Created by Nathan Palmer on 2008-02-26.
Copyright (c) 2008 Nathan Palmer. All rights reserved.
"""

import os

#Defines opposite cardinal directions
oppositeDirs = {"east" : "west",
                "west" : "east",
                "north": "south",
                "south": "north",
                "up"   : "down",
                "down" : "up"}
                
PATH_TO_INPUT_SPEC = os.path.join('xml', 'relaxng-hw5.rng')
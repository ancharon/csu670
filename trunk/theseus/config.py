#!/usr/bin/env python
# encoding: utf-8
"""
config.py
This file is meant to hold global variables for use throughout the program.

Copyright (c) 2008 Nathan Palmer, Ethan Caldwell, David Fier. All rights reserved.
"""

import os

#Defines opposite cardinal directions
OPPOSITE_DIRS = {"east" : "west",
                "west" : "east",
                "north": "south",
                "south": "north",
                "up"   : "down",
                "down" : "up"}
                

#Infinity is defined here as 1e3000. We know that's not true.
# Unfortunately the "right" way to do infinity isn't guaranteed to be available until Python 2.6.
#INFINITY = float("infinity")
INFINITY = 1e3000

#Path the specification for input XML.
#PATH_TO_INPUT_SPEC = os.path.join('xml', 'relaxng-hw5.rng')
PATH_TO_INPUT_SPEC = os.path.join('xml', 'relaxng-hw7.rng')

#Validation is a huge performance hit. If you're confident that the program
# will be getting XML that validates to the given specification, set this to 
# False (with a capital F) for a big speed boost.
VALIDATE=True
#VALIDATE = False
#!/usr/bin/env python
# encoding: utf-8
"""
build.py

Copyright (c) 2008 Nathan Palmer, Ethan Caldwell, David Fier. All rights reserved.
"""

import os

os.system("python freeze/freeze.py -o exec -x pydoc theseus.py")
os.chdir("exec")
os.system("make")
os.chdir("..")
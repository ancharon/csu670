#!/usr/bin/env python
import os

os.system("python freeze/freeze.py -o exec -x pydoc theseus.py")
os.chdir("exec")
os.system("make")
os.chdir("..")
#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Nathan Palmer on 2008-02-22.
Copyright (c) 2008 Nathan Palmer. All rights reserved.
LOL DAVE WUZ HERE
"""

import sys,os
from xml import sax
import unittest
import gameparser


class main:
    def __init__(self):
        castle = gameparser.Castle()

if __name__ == '__main__':
    
    myParser = gameparser.Xml2Obj()
    #The Parse method returns the root element of the XML tree
    try:
        specname = os.path.join('xml', 'relaxng-hw5.rng')
        if len(sys.argv) > 1: #There is an argument
            element = myParser.Parse(sys.argv[1], specname)
        else:
            element = myParser.Parse(None, specname)
        print element.toString()
    except sax.SAXException,message:
        print message

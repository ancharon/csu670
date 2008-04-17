#!/usr/bin/env python
# encoding: utf-8
"""
gameparser.py

Copyright (c) 2008 Nathan Palmer, Ethan Caldwell, David Fier. All rights reserved.
"""


# This script takes an XML file from stdin expected to be in the format 
# specified by the file 'relaxng.rng'. It prints a human-readable description
# of the input to stdout.

import string
import sys,os
from xml import sax
import unittest
import logging

import graph
import config
        
#Element and Xml2Obj were originally written by John Bair and are freely 
#available on the ActiveState Programmers' Network (ASPN) at
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/149368
#I've slightly modified them so that we'll (hopefully) be able to use Python's
#IncrementalParser when we have to deal with input stream instead of a file
class Element(object):    
    '''A generic parsed XML element'''
   
    def __init__(self,name,attributes,generateType):
        if name != None:
            'Element constructor'
            # The element's tag name
            self.name = name
            # The element's attribute dictionary
            self.attributes = attributes
            # The element's cdata
            self.cdata = ''
            # The element's child element list (sequence)
            self.children = []
            # The type of object that represents this Element
            self.generateType = generateType         
        
    def AddChild(self,element):
        '''Add a reference to a child element'''
        self.children.append(element)
        
    def getAttribute(self,key):
        '''Get an attribute value'''
        return self.attributes.get(key)
    
    def getData(self):
        '''Get the cdata'''
        return self.cdata
        
    def getElements(self,name=''):
        '''Get a list of child elements'''
        #If no tag name is specified, return the all children
        if not name:
            return self.children
        else:
            # else return only those children with a matching tag name
            elements = []
            for element in self.children:
                if element.name == name:
                    elements.append(element)
            return elements
            
    def objectify(self):
        '''Instantiates, initializes, and returns an object of type self.generateType.'''
        gameElement = self.generateType()
        gameElement.initialize(self)
        return gameElement
            
class Xml2Obj(sax.ContentHandler):
    '''XML to Object'''
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        self.root = None
        self.nodeStack = []
        
    def makeElement(self, name, attributes):
        #TODO: find a better place for the typeMappings dictionary
        typeMappings = {"room":     graph.Room,
                        "gameover": graph.Gameover,
                        "outside":  graph.Outside,
                        "frog":     graph.Frog,
                        "paper":    graph.Paper,
                        "treasure": graph.Treasure,
                        "shield":   graph.Shield,
                        "weapon":   graph.Weapon,
                        "character":graph.Character
                        }
        if name in typeMappings:
            element = Element(name, attributes, typeMappings[name])
        else:
            element = Element(name,attributes, None)
        
        return element
        
    def startElement(self,name,attributes):
        'SAX start element event handler'
        # Instantiate the appropriate Element object or a subclass of element
        element = self.makeElement(name, attributes)
        
        # Push element onto the stack and make it a child of parent
        if len(self.nodeStack) > 0:
            parent = self.nodeStack[-1]
            parent.AddChild(element)
        else:
            self.root = element
        self.nodeStack.append(element)
        
    def endElement(self,name):
        '''SAX end element event handler'''
        self.nodeStack = self.nodeStack[:-1]

    def characters(self,data):
        '''SAX character data event handler'''
        if string.strip(data):
            #This data is not just white space
            data = data
            element = self.nodeStack[-1]
            element.cdata += data
            return

    def Parse(self,filename,specname):
        'Parse the input from filename (which can also be a stream)'
        # Create a SAX parser
        Parser = sax.make_parser()
        handler = self
   
        #If the filename doesn't exist, we'll need to try reading from stdin
        #to get some XML to validate.
        if filename is None:
            filename = "temp.xml"
            file = open(filename,'w')
            while 1:
                line = sys.stdin.readline()
                file.write(line)
                #We're done parsing if this line signals the end of a game
                # object description.
                if line.strip() in config.ELEMENT_END_SYMBOLS:
                    break
            logging.debug("Closing File " + filename)
            file.close()
        elif not os.path.exists(filename):
            errorMsg = u"Error: file '" + filename + "' not found\n"
            logging.error(errorMsg)
            sys.exit(1)
                
        #Use Jing to validate our Relax NG because we're too lazy to validate
        #it ourselves -- that's a lot of work.
        if config.VALIDATE:
            command = "java -jar jing.jar " + specname + " " + filename
            result = os.system(command)
            
        if not config.VALIDATE or result is 0:
            #Parse the XML File
            ParserStatus = sax.parse(open(filename,"r"), handler)
        else:
            logging.error("ERROR: Given XML does not pass validation.")
            raise sax.SAXException("ERROR: Given XML does not pass validation.")
        
        #Set the type-specific properties of this element
        element = self.root.objectify()
        
        return element

def printElements(element, level):
    'Output an element and all of its sub-elements'
    if element.name in ('treasure', 'shield','weapon'):
        print (" " * (level * 4)) + element.name + " '" + element.getAttribute('style') + "': " + element.getData()
    else:
        print (" " * (level * 4)) + element.name + ": " + element.getData()
    subnodes = element.getElements()
    for subnode in subnodes:
        printElements(subnode, level + 1)
        
#A little Python magic that allows this program to run as a stand-alone script
if __name__ == '__main__':
    myParser = Xml2Obj()
    element = myParser.Parse('xml/fullroom.xml', config.PATH_TO_INPUT_SPEC)
    printElements(myParser.root, 1)

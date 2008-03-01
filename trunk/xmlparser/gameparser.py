#!/usr/bin/env python

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
    '''A parsed XML element'''
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
        
    def startElement(self,name,attributes):
        'SAX start element event handler'
        # Instantiate the appropriate Element object or a subclass of element
        if name == "room":
            element = Element(name, attributes, graph.Room)
        elif name == "gameover":
            element = Element(name, attributes, graph.Gameover)
        else:
            element = Element(name,attributes, None)
        
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
                if (line.strip() == "</room>") or (line.strip() == "</gameover>"):
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
    print (" " * (level * 4)) + element.name + ": " + element.getData()
    subnodes = element.getElements()
    for subnode in subnodes:
        printElements(subnode, level + 1)
        
#FIXME: Need unit tests for classes   
# class Xml2ObjTests(unittest.TestCase):
    # def setUp(self):
        # pass
        
# class ElementTests(unittest.TestCase):
    # def setUp(self):
        # pass
           
        
#A little Python magic that allows this program to run as a stand-alone script
if __name__ == '__main__':
    unittest.main()

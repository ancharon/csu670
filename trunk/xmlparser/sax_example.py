#!/usr/bin/env python

#This script takes an XML file expected to be in the format specified by the
# following RELAX NG specification:
# <element name="messages" xmlns="http://relaxng.org/ns/structure/1.0">
  # <zeroOrMore>
    # <element name="room">
      # <interleave>
        # <element name="purpose">
          # <text/>
        # </element>
        # <zeroOrMore>
          # <element name="characteristic">
            # <text/>
          # </element>
        # </zeroOrMore>
        # <element name="exits">
          # <zeroOrMore>
            # <choice>
              # <value>up</value>
              # <value>down</value>
              # <value>north</value>
              # <value>south</value>
              # <value>east</value>
              # <value>west</value>
            # </choice>
          # </zeroOrMore>
        # </element>
      # </interleave>
    # </element>
  # </zeroOrMore>
  # <element name="gameover">
    # <element name="outcome">
      # <text/>
    # </element>
  # </element>
# </element>

import string
from xml.parsers import expat
from xml import sax

XML_TREE_ROOT = None

class Castle(object):
    #Holds onto a representation of the castle, made up of rooms
    
    def __init__(self):
        self.rooms = []
        
    def getRooms(self):
        return self.rooms
        
    def addRoom(self, room):
        self.rooms.append(room)

class Room(object):
    
    def __init__(self):
        #Sets up empty values for the room object
        self.purpose = ""
        self.characteristics = []
        self.exits = []
        return
        
    def setPurpose(self, purpose):
        self.purpose = purpose
        return
        
    def getPurpose(self):
        return self.purpose
        
    def addCharacteristic(self, characteristic):
        self.characteristics.append(characteristic)
        return
        
    def getCharacteristics(self):
        return self.characteristics
        
    def addExit(self, exit):
        self.exits.append(exit)
        return
        
    def getExits(self):
        return exits
    
    def toString(self):
        print "The room is a " + self.purpose
        if characteristics:
            print "It has the following characteristics:"
            for char in characteristics:
                print char
        if exits:
            print "There are exits in the following directions:"
            for exit in exits:
                print exit
        return

        
#Element and Xml2Obj were originally written by John Bair and are freely 
#available on the ActiveState Programmers' Network (ASPN) at
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/149368
#I've slightly modified them so that we'll (hopefully) be able to use Python's
#IncrementalParser when we have to deal with input stream instead of a file
class Element:    
    'A parsed XML element'
    def __init__(self,name,attributes):
        'Element constructor'
        # The element's tag name
        self.name = name
        # The element's attribute dictionary
        self.attributes = attributes
        # The element's cdata
        self.cdata = ''
        # The element's child element list (sequence)
        self.children = []
        
    def AddChild(self,element):
        'Add a reference to a child element'
        self.children.append(element)
        
    def getAttribute(self,key):
        'Get an attribute value'
        return self.attributes.get(key)
    
    def getData(self):
        'Get the cdata'
        return self.cdata
        
    def getElements(self,name=''):
        'Get a list of child elements'
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
            
class Xml2Obj(sax.ContentHandler):
    'XML to Object'
    def __init__(self):
        self.root = None
        self.nodeStack = []
        
    def startElement(self,name,attributes):
        'SAX start element even handler'
        # Instantiate an Element object
        element = Element(name.encode(),attributes)
        
        # Push element onto the stack and make it a child of parent
        if len(self.nodeStack) > 0:
            parent = self.nodeStack[-1]
            parent.AddChild(element)
        else:
            self.root = element
        self.nodeStack.append(element)
        
    def endElement(self,name):
        'SAX end element event handler'
        self.nodeStack = self.nodeStack[:-1]

    def characters(self,data):
        'SAX character data event handler'
        if string.strip(data):
            data = data.encode()
            element = self.nodeStack[-1]
            element.cdata += data
            return

    def Parse(self,filename):
        # Create a SAX parser
        Parser = sax.make_parser()
        handler = self

        # Parse the XML File
        ParserStatus = sax.parse(open(filename,'r'), handler)
        
        return self.root

def printElements(element, level):
    print (" " * (level * 4)) + element.name + ": " + element.getData()
    subnodes = element.getElements()
    for subnode in subnodes:
        printElements(subnode, level + 1)
        
        
#A little Python magic that allows this program to run as a stand-alone script
if __name__ == '__main__':
    parser = Xml2Obj()
    element = parser.Parse('test_message.xml')

    printElements(element, 0)
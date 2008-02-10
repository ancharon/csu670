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
from xml import sax

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

class Element:
    #This class was written by John Bair and is freely available from the 
    #ActiveState Programmers' Network (ASPN) at
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/149368
    
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
            
    def toString(self, level=0):
        retval = " " * level
        retval += "<%s" % self.name
        c = ""
        for child in self.children:
            c += child.toString(level+1)
        if c == "":
            retval += "/>\n"
        else:
            retval += ">\n" + c + ("</%s>\n" % self.name)
        return retval

class MessageHandler(sax.ContentHandler):
    #A class that handles XML events and draws a tree from the document structure
    
    def __init__(self, nodeStack):
        self.root = None
        self.nodeStack = nodeStack
        
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
        
    def characters(self, text):
        if string.strip(text):
            text = text.encode()
            element = self.nodeStack[-1]
            element.cdata += text
            return

    # def startDocument(self):
        # print "--- [Document]"
        # self.depth = self.depth + 1
        # return

    # def startElement(self, name, attributes):
        # print self.increment*self.depth + "+-- [Element <" + name + ">]"            
        # self.depth = self.depth + 1
        # if name == "room":
            # currentRoom = Room()
        # elif currentRoom:
            #We're parsing a room element
            # self.setRoomElement(name)
        # return

    # def endElement(self, name):
        # self.depth = self.depth - 1
        # if name == "room":
            # castle.addRoom(currentRoom)
            # currentRoom = None
        # return
        
#A little Python magic that allows this program to run as a stand-alone script
if __name__ == '__main__':
    #Create a new parser instance, using the Incremental Parser
    #This will allow us to parse partial files using the feed() method
    # For now, we're not making use of that.
    parser = sax.make_parser()
    #After parsing, nodestack will be a list of Elements
    nodestack = []
    #Create an instance of our handler class, which will be registered
    #to receive SAX events
    handler = MessageHandler(nodestack)
    #Pass a file to be parsed, and pass the handler to be registered
    #to receive SAX events.
    f = open("test_message.xml")
    sax.parse(f, handler)
    #At this point, the parser has completed processing, and all events
    #have been dispatched.  We're done.
    f.close()
    for node in nodestack:
        print node.toString()
        
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
import sys,os
from xml import sax
#from lxml import etree
from StringIO import StringIO

class Castle(object):
    #Holds onto a representation of the castle, made up of rooms
    
    def __init__(self):
        self.rooms = []
        
    def getRooms(self):
        return self.rooms
        
    def addRoom(self, room):
        self.rooms.append(room)



        
#Element and Xml2Obj were originally written by John Bair and are freely 
#available on the ActiveState Programmers' Network (ASPN) at
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/149368
#I've slightly modified them so that we'll (hopefully) be able to use Python's
#IncrementalParser when we have to deal with input stream instead of a file
class Element(object):    
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
            
class Room(Element):
    
    def __init__(self, name, attributes):
        super(Room, self).__init__(name=name, attributes=attributes) 
        #Sets up empty values for the room object
        self.purpose = ""
        self.characteristics = []
        self.exits = []
        
        return
        
    def setPurpose(self, purpose):
        self.purpose = unicode(purpose)
        return
        
    def getPurpose(self):
        return self.purpose
        
    def addCharacteristic(self, characteristic):
        self.characteristics.append(unicode(characteristic))
        return
        
    def getCharacteristics(self):
        return self.characteristics
        
    def addExit(self, exit):
        self.exits.append(unicode(exit))
        return
        
    def getExits(self):
        return self.exits
    
    def toString(self):
        print "This room is a " + self.purpose
        if characteristics:
            print "It has the following characteristics:"
            for char in characteristics:
                print char
        if exits:
            print "There are exits in the following directions:"
            for exit in exits:
                print exit
        return
        
class Gameover(Element):
    
    def __init__(self, name, attributes):
        super(Gameover, self).__init__(name=name, attributes=attributes)
        self.outcome = ""
        
    def setOutcome(self, outcome):
        self.outcome = unicode(outcome)
        
    def getOutcome(self):
        return self.outcome
            
class Xml2Obj(sax.ContentHandler):
    'XML to Object'
    def __init__(self):
        self.root = None
        self.nodeStack = []
        
    def startElement(self,name,attributes):
        'SAX start element event handler'
        # Instantiate the appropriate Element object or a subclass of element
        if name == "room":
            element = Room(name.encode(), attributes)
        elif name == "gameover":
            element = Gameover(name.encode(), attributes)
        else:
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
            #This data is not just white space
            data = data.encode()
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
            for line in sys.stdin.readlines():
                file.write(line)
                
        #Use Jing to validate our Relax NG because we're too lazy to validate
        #it ourselves -- that's a lot of work.
        command = "java -jar jing.jar " + specname + " " + filename
        result = os.system(command)

        if result is 0:
            #Parse the XML File
            ParserStatus = sax.parse(open(filename,"r"), handler)
        else:
            raise sax.SAXException("Given XML does not pass validation.")
        
        return self.root

def printElements(element, level):
    print (" " * (level * 4)) + element.name + ": " + element.getData()
    subnodes = element.getElements()
    for subnode in subnodes:
        printElements(subnode, level + 1)
        
def storeElements(element, level):
    #This method stores element data in the more Pythonic Room class
    #For now, it also prints out everything about the room for debugging purposes.
    #Much of this method should be abstracted out/put in a class or two.
    children = element.getElements()
    for child in children:
        if type(child) == Room:
            #Get a list of room properties (the child's children)
            roomProperties = child.getElements()
            for prop in roomProperties:
                #Assign the Room properties according to the element data
                if prop.name == "purpose":
                    child.setPurpose(prop.cdata.strip())
                elif prop.name == "characteristic":
                    child.addCharacteristic(prop.cdata.strip())
                elif prop.name == "exits":
                    exitList = prop.cdata.split()
                    for exit in exitList:
                        child.addExit(exit)
            print u"This room is a " + child.getPurpose() + "."
            print u"It has the following characteristics: "
            for char in child.getCharacteristics():
                print char
            print u"It has the following exits: "
            for exit in child.getExits():
                print exit
            print
        elif type(child) == Gameover:
            gameoverProperties = child.getElements()
            for prop in gameoverProperties:
                #There should be only one, outcome
                if prop.name == "outcome":
                    child.setOutcome(prop.cdata.strip())
            print u"The game is over."
            print u"Outcome: " + child.getOutcome()
        storeElements(child, level + 1)
        
        
#A little Python magic that allows this program to run as a stand-alone script
if __name__ == '__main__':
    parser = Xml2Obj()
    #The Parse method returns the root element of the XML tree
    try:
        element = parser.Parse(None, 'relaxng.rng')
        storeElements(element, 0)
    except sax.SAXException,message:
        print message
        pass
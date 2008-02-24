#!/usr/bin/env python

# This script takes an XML file from stdin expected to be in the format 
# specified by the file 'relaxng.rng'. It prints a human-readable description
# of the input to stdout.

import string
import sys,os
from xml import sax
import unittest

#FIXME: Castle should be in its own module (with Room)
class Castle(object):
    '''A representation of the castle, made up of rooms'''
    
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
    '''A parsed XML element'''
    def __init__(self,name,attributes):
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

#FIXME: Room should be in a separate module (with Castle)  
class Room(Element):
    '''A single room in a castle. Parsed from input.'''
    
    def __init__(self, name=None, attributes=None):
        super(Room, self).__init__(name=name, attributes=attributes) 
        #Sets up empty values for the room object
        self.purpose = ""
        self.characteristics = set()
        self.exits = set()
        return
        
    def setPurpose(self, purpose):
        self.purpose = unicode(purpose)
        return
        
    def getPurpose(self):
        return self.purpose
        
    def addCharacteristic(self, characteristic):
        self.characteristics.add(unicode(characteristic))
        return
        
    def getCharacteristics(self):
        return self.characteristics
        
    def addExit(self, exit):
        self.exits.add(unicode(exit))
        return
        
    def getExits(self):
        return self.exits
        
    def isEqual(self, otherRoom):
        if (otherRoom.purpose == self.purpose) and \
           (self.characteristics == otherRoom.characteristics):
            return True
        else:
            return False
            
    def isNull(self):
        if self.purpose:
            return False
        else: 
            return True
        
    def objectify(self):
        '''Sets the Room-specific properties of this object'''
        roomProperties = self.getElements()
        for prop in roomProperties:
            #Assign the Room properties according to the element data
            if prop.name == "purpose":
                self.setPurpose(prop.cdata.strip())
            elif prop.name == "characteristic":
                self.addCharacteristic(prop.cdata.strip())
            elif prop.name == "exits":
                #FIXME: Spec has changed, exits now has exit children.
                exitList = prop.getElements()
                for exit in exitList:
                    self.addExit(exit.cdata.strip())
    
    def toString(self):
        returnString = ""
        returnString = u"This room is a " + self.getPurpose() + os.linesep
        if self.getCharacteristics():
            returnString += u"It has the following characteristics:" + os.linesep
            for char in self.getCharacteristics():
                returnString += char + os.linesep
        if self.getExits():
            returnString += u"There are exits in the following directions:" + os.linesep
            for exit in self.getExits():
                returnString += exit + os.linesep
        return returnString
        
class Gameover(Element):
    '''A game over message. Parsed from input.'''
    
    def __init__(self, name, attributes):
        super(Gameover, self).__init__(name=name, attributes=attributes)
        self.outcome = ""
        
    def setOutcome(self, outcome):
        self.outcome = unicode(outcome)
        
    def getOutcome(self):
        return self.outcome
        
    def objectify(self):
        'Sets the Gamover-specific properties of this object'
        gameoverProperties = self.getElements()
        for prop in gameoverProperties:
            #There should be only one, outcome
            if prop.name == "outcome":
                self.setOutcome(prop.cdata.strip())
        
    def toString(self):
        returnString = u"The game is over." + os.linesep
        returnString += u"Outcome: " + self.getOutcome() + os.linesep
        return returnString
            
class Xml2Obj(sax.ContentHandler):
    '''XML to Object'''
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
        '''SAX end element event handler'''
        self.nodeStack = self.nodeStack[:-1]

    def characters(self,data):
        '''SAX character data event handler'''
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
            file.close()
        elif not os.path.exists(filename):
            errorMsg = u"Error: file '" + filename + "' not found\n"
            sys.stderr.write(errorMsg)
            sys.exit(1)
                
        #Use Jing to validate our Relax NG because we're too lazy to validate
        #it ourselves -- that's a lot of work.
        command = "java -jar jing.jar " + specname + " " + filename
        result = os.system(command)

        if result is 0:
            #Parse the XML File
            ParserStatus = sax.parse(open(filename,"r"), handler)
        else:
            raise sax.SAXException("ERROR: Given XML does not pass validation.")
        
        #Set the type-specific properties of this element
        self.root.objectify()
        
        return self.root

def printElements(element, level):
    print (" " * (level * 4)) + element.name + ": " + element.getData()
    subnodes = element.getElements()
    for subnode in subnodes:
        printElements(subnode, level + 1)
        
#FIXME: Need unit tests for classes   
# class Xml2ObjTests(unittest.TestCase):
    # def setUp(self):
        # pass
        
class RoomTests(unittest.TestCase):
    '''Tests for the Room class'''
    
    def setUp(self):
        self.room1 = Room('dummy', {})
        self.room1.setPurpose("dungeon")
        self.room1.addCharacteristic("dark")
        self.room1.addCharacteristic("dank")
        self.room1.addCharacteristic("deep")
        self.room1.addExit("north")
        
        self.room2 = Room('stuff', {})
        self.room2.setPurpose("dungeon")
        self.room2.addCharacteristic("deep")
        self.room2.addCharacteristic("dank")
        self.room2.addCharacteristic("dark")
        self.room2.addExit("north")
        
    def testIsEqual(self):
        result = self.room1.isEqual(self.room2)
        self.assertEqual(result, True)
        
        #Test against room characteristics
        self.room1.addCharacteristic("smelly")
        result = self.room1.isEqual(self.room2)
        self.assertEqual(result, False)
        
        self.room2.addCharacteristic("smelly")
        result = self.room1.isEqual(self.room2)
        self.assertEqual(result, True)
        
        #Test against room purpose
        self.room2.setPurpose("fountain")
        result = self.room1.isEqual(self.room2)
        self.assertEqual(result, False)

# class GameOverTests(unittest.TestCase):
    # def setUp(self):
        # pass
        
# class ElementTests(unittest.TestCase):
    # def setUp(self):
        # pass
        
# class CastleTests(unittest.TestCase):
    # def setUp(self):
        # pass
           
        
#A little Python magic that allows this program to run as a stand-alone script
if __name__ == '__main__':
    unittest.main()

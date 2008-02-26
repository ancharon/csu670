#!/usr/bin/env python

import sys, os
import unittest

#FIXME: Room and Gameover should be somewhere else (perhaps a gameelements module?)  
class Room(object):
    '''A single room in a castle. Parsed from input.'''
    
    def __init__(self):
        #Sets up empty values for the room object
        self.purpose = ""
        self.characteristics = set()
        self.exits = set()
        return
        
    def initialize(self, xmlElement):
        '''Initialize this Room's attributes using data from parsed XML element'''
        roomProperties = xmlElement.getElements()
        for prop in roomProperties:
            #Assign the Room properties according to the element data
            if prop.name == "purpose":
                self.setPurpose(prop.cdata.strip())
            elif prop.name == "characteristic":
                self.addCharacteristic(prop.cdata.strip())
            elif prop.name == "exits":
                exitList = prop.getElements()
                for exit in exitList:
                    self.addExit(exit.cdata.strip())
        
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
    
    #FIXME: exits should be Edges, not strings. Use the incoming string to
    # create an Edge.    
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
        
class Gameover(object):
    '''A game over message. Parsed from input.'''

    def __init__(self):
        self.outcome = ""

    def setOutcome(self, outcome):
        self.outcome = unicode(outcome)

    def getOutcome(self):
        return self.outcome

    def initialize(self, xmlElement):
        gameoverProperties = xmlElement.getElements()
        for prop in gameoverProperties:
            #There should be only one, outcome
            if prop.name == "outcome":
                self.setOutcome(prop.cdata.strip())

    def toString(self):
        returnString = u"The game is over." + os.linesep
        returnString += u"Outcome: " + self.getOutcome() + os.linesep
        return returnString


class Edge(object):
    
    def __init__(self, direction, (node1, node2)):
        '''An edge means that to get from node1 to node2, you go direction'''
        self.direction = direction
        self.nodes = (node1, node2)
        
    def getNodes(self):
        return self.nodes
       
    def getDirection(self):
        return self.direction
        
    def setNodes(self, (node1, node2)):
        self.nodes = (node1, node2)
        
    def setDirection(self):
        self.direction = direction

#FIXME: This class shouldn't exist, use Room instead.
class Node(object):
    
    def __init__(self, room):
        self.room = room  

    def getExits(self):
        return self.room.getExits()


#FIXME: eliminate all mentions of Node, replace with Room
class Graph(object):

    def __init__(self):
        self.rooms = set()
        self.edges = set()
        pass
        
    def addEdges(self, room):
        for exit in room.getExits():
            self.addEdge(exit, (self, Room()))
        return self.room.exits()
        
    def addEdge(self, direction, (node1, node2)):
        #FIXME: If there is already an edge going in this direction from node 1 to a non-null node,
        # then don't add anything. Otherwise, add this new edge.
        self.edges.add(Edge(direction, (node1, node2)))
        
    def addRoom(self, room):
        self.rooms.add(room)
        self.addEdges(room)
        
class RoomTests(unittest.TestCase):
    '''Tests for the Room class'''

    def setUp(self):
        self.room1 = Room()
        self.room1.setPurpose("dungeon")
        self.room1.addCharacteristic("dark")
        self.room1.addCharacteristic("dank")
        self.room1.addCharacteristic("deep")
        self.room1.addExit("north")

        self.room2 = Room()
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

#FIXME: Unit tests needed

if __name__ == "__main__":
    unittest.main()
        
    
    
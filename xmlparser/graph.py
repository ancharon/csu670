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
        #Exits are strings, which will be used later to create edges
        self.exits = set()
        #The room will be told what edges it has. This is a performance
        #optimization, it helps avoid having to search through all the edges
        #in the graph.
        self.edges = {}
        #Set to True once we've visited this room in our graph traversal.
        self.visited = False
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
        
    #FIXME: This method should probably not exist. We don't want people changing
    # this stuff after it's been parsed.
    def setPurpose(self, purpose):
        self.purpose = unicode(purpose)
        return
        
    def getPurpose(self):
        return self.purpose
        
    #FIXME: This method should probably not exist. We don't want people changing
    # this stuff after it's been parsed.
    def addCharacteristic(self, characteristic):
        self.characteristics.add(unicode(characteristic))
        return
        
    def getCharacteristics(self):
        return self.characteristics
       
    #FIXME: This method should probably not exist. We don't want people changing
    # this stuff after it's been parsed.
    def addExit(self, exit):
        self.exits.add(unicode(exit))
        return
        
    def getAnExit(self):
        #FIXME: horrible.
        temp = self.exits.copy()
        return temp.pop()
        
    def getExits(self):
        return self.exits
        
    def addEdge(self, edge):
        self.edges[edge.getDirection()] = edge
        
    def removeEdge(self, edge):
        del self.edges[edge.getDirection()]
        
    def getEdges(self):
        return self.edges
        
    def getEdge(self, direction):
        return self.edges[direction]
        
    def isVisited(self):
        return self.visited
        
    def visit(self):
        self.visited = True
        
    def isEqual(self, otherRoom):
        '''Rooms are considered equal if they have the same purpose and characteristics'''
        if (otherRoom.purpose == self.purpose) and \
           (self.characteristics == otherRoom.characteristics):
            return True
        else:
            return False
    
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

    #FIXME: This method should probably not exist. We don't want people changing
    # this stuff after it's been parsed.
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
    
    def __init__(self, direction, (room1, room2)):
        '''An edge means that to get from room1 to room2, you go direction'''
        self.direction = direction
        self.rooms = (room1, room2)
        
    def getRooms(self):
        return self.rooms
       
    def getDirection(self):
        return self.direction
        
    def setRooms(self, (room1, room2)):
        self.rooms = (room1, room2)
        
    def setDirection(self):
        self.direction = direction
        
    def isEqual(self, edge):
        #Two edges are equal if:
        # 1. Their directions are the same
        # 2. Edge1.room1 = Edge2.room1
        # 3. Edge2.room2 = Edge2.room2
        if self.direction == edge.direction:
            myRooms = self.getRooms()
            yourRooms = edge.getRooms()
            if  myRooms[0].isEqual(yourRooms[0]) and \
                myRooms[1].isEqual(yourRooms[1]):
                return True
        return False


class Graph(object):

    def __init__(self):
        self.rooms = set()
        self.edges = set()
        pass
        
    def addEdge(self, direction, (room1, room2)):
        #FIXME: If there is already an edge going in this direction from node 1 to a non-null node,
        # then don't add anything. Otherwise, add this new edge.
        newEdge = Edge(direction, (room1, room2))
        if room2 is not None:
            #There is an edge here already. Check if it's equal to the new one.
            oldEdge = room1.getEdge(direction)
            if newEdge.isEqual(oldEdge):
                #They're the same, do nothing.
                return
            else:
                #They're not the same , get rid of the old one.
                self.removeEdge(oldEdge)
        #Add the edge to both the graph and the room
        self.edges.add(newEdge)
        room1.addEdge(newEdge)
            
    def removeEdge(self, edge):
        room = edge.getRooms()[0]
        self.edges.remove(edge)
        room.removeEdge(edge())
        
                    
    def addRoom(self, room):
        self.rooms.add(room)
        #New rooms are populated with edges going to null. It is the
        #responsibility of the GamePlayer class to update them later.
        for exit in room.getExits():
            self.addEdge(exit, (room, None))
        #Mark the room as visited
        room.visit()
        
    def isNewRoom(room):
        '''Returns True if this room is not in the graph, False otherwise'''
        return not room.isVisited()
        
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

class GameOverTests(unittest.TestCase):
    def createGameOver(self):
		self.setOutcome(self, "Game Over")
		
    #Test if setOutcome has assigned an outcome.  Should only be the case on Game Over.  Result true if game is over.
	def testIsGameOver(self):
		result = (self.outcome is not "")
		self.assertEqual(result, True)
			
class EdgeTests(unittest.TestCase):
	def setUp(self):
	    self.room1 = Room()
        self.room1.setPurpose("bedroom")
        self.room1.addCharacteristic("creepy")
        self.room1.addCharacteristic("dim")
        self.room1.addCharacteristic("arid")
        self.room1.addExit("north")

        self.room2 = Room()
        self.room2.setPurpose("dining hall")
        self.room2.addCharacteristic("large")
        self.room2.addCharacteristic("ornate")
        self.room2.addCharacteristic("festive")
        self.room2.addExit("south")
		
	#Test that edges exist
		self.assertEqual(self.edges != set(), True)
		
	def testEdge(self):
if __name__ == "__main__":
    unittest.main()
        
    
    

#!/usr/bin/env python
# encoding: utf-8
"""
graph.py

Copyright (c) 2008 Nathan Palmer, Ethan Caldwell, David Fier. All rights reserved.
"""

import sys, os
import unittest
import logging
import random
import config

#TODO: implement all these classes
#Each must have an initialize method.
class Item(object):
    '''An item in the castle. Meant to be subclassed.'''
    pass
    
class Frog(Item):
    pass
    
class Paper(Item):
    pass
    
class Treasure(Item):
    pass
    
class Shield(Item):
    pass
    
class Weapon(Item):
    pass
    
class Character(object):
    '''A character in the castle. Parsed from input.'''
    pass
    
class Outside(object):
    pass

class Room(object):
    '''A single room in a castle. Parsed from input.'''
    
    # ------------------------- Initialization -------------------------
    
    def __init__(self):
        '''Constructor for Room class'''
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
    
    # ------------------------- Getters and setters -------------------------
        
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

    def getExits(self):
        return self.exits
        
    def addEdge(self, edge):
        #FIXME: Should be deprecated; see notes in Edge class
        self.edges[edge.getDirection()] = edge
        
    def removeEdge(self, edge):
        #FIXME: Should be deprecated; see notes in Edge class
        del self.edges[edge.getDirection()]
        
    def getEdges(self):
        #FIXME: should be deprecated; see notes in Edge class
        edgeList = []
        for edge in self.edges:
            edgeList.append(self.edges[edge])
        return edgeList
        
    def getEdge(self, direction):
        #FIXME: Should be deprecated; see notes in Edge class
        return self.edges[direction]
        
    def isVisited(self):
        return self.visited
        
    def visit(self):
        self.visited = True

    #  ------------------------- More interesting stuff -------------------------
        
    def getAnExit(self):
        '''Returns a random exit from this Room's exit collection'''
        #FIXME: Horrible. This method is a last resort and really should never
        # be called. Any time it is, we should be also logging an error.
        temp = []
        for exit in self.exits:
            temp.append(exit)
        r = random.randint(0, len(temp)-1)            
        return temp[r]
                
    def hasUnexploredExits(self):
        '''Returns true if it has at least one unexplored exit (see the Edge class for a definition
           of unexplored exit)'''
        #FIXME: This should be changed to use the internal exits collection instead of deprecated Edges
        for edge in self.getEdges():
            if edge.isExplored():
                return True
        return False
        
    def isEqual(self, otherRoom):
        '''Rooms are considered equal if they have the same purpose and characteristics'''
        if self is None or otherRoom is None:
            return False
        if (self.purpose  == otherRoom.purpose) and \
           (self.characteristics == otherRoom.characteristics) and \
           (self.exits == otherRoom.exits):
            return True
        else:
            return False
    
    def toString(self):
        '''Produces a human-readable string representation of this Room object'''
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

    # ------------------------- Initialization -------------------------
    
    def __init__(self):
        '''Constructor for Gameover class'''
        self.outcome = ""
        
    def initialize(self, xmlElement):
        '''Initializes the Gameover's attributes using data from parsed XML element'''
        gameoverProperties = xmlElement.getElements()
        for prop in gameoverProperties:
            #There should be only one, outcome
            if prop.name == "outcome":
                self.setOutcome(prop.cdata.strip())
                
    # ------------------------- Getters and setters -------------------------

    #FIXME: This method should probably not exist. We don't want people changing
    # this stuff after it's been parsed.
    def setOutcome(self, outcome):
        self.outcome = unicode(outcome)

    def getOutcome(self):
        return self.outcome
                
    # ------------------------- More interesting stuff -------------------------

    def toString(self):
        '''Produces a human-readable string representation of this Gameover object'''
        returnString = u"The game is over." + os.linesep
        returnString += u"Outcome: " + self.getOutcome() + os.linesep
        return returnString


class Edge(object):
    '''Represents a doorway between two Rooms in the castle.'''
    #FIXME: The Edge class just makes a huge amount of trouble, seriously. 
    # It should probably be deprecated in favor of internal exit collections inside the Room class.
    
    # ------------------------- Initialization -------------------------
    
    def __init__(self, direction, (room1, room2)):
        '''Constructor for the Edge class - "An edge means that to get from [room1] to [room2], you go [direction]"'''
        #NOTE: This is an actual data structure made by us, not parsed from XML, so there's no need for a separate initialization call.
        self.direction = direction
        self.rooms = (room1, room2)
        self.weight = 1 #unweighted graph
        
    # ------------------------- Getters and setters -------------------------
        
    def getRooms(self):
        return self.rooms
        
    def getOrigin(self):
        return self.rooms[0]
        
    def getDestination(self):
        return self.rooms[1]
       
    def getDirection(self):
        return self.direction
        
    def setRooms(self, (room1, room2)):
        self.rooms = (room1, room2)
        
    def setDirection(self):
        self.direction = direction
    
    # ------------------------- More interesting stuff -------------------------
    
    def isExplored(self):
        '''Returns True iff room2 - the "to" room - is not null, meaning it has been visited before'''
        #This looks retarded, but it works, honest. If rooms[1] is None, then we haven't been there (duh), and None = False in Python.
        return self.rooms[1]
    
    def isEqual(self, edge):
        '''Determines if a given edge is the same as this one. See comments for explicit specification.'''
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
        
    def toString(self):
        '''Produces a human-readable string representation of this Edge object'''
        toReturn = ""
        toReturn += "Edge from "
        toReturn += unicode(self.rooms[0]) + " to " + unicode(self.rooms[1])
        toReturn += " going " + self.direction
        return toReturn


class Graph(object):
    '''Represents every Room and Edge (doorway between Rooms) seen thus far.'''

    # ------------------------- Initialization -------------------------
    
    def __init__(self):
        '''Constructor for the Graph object'''
        logging.basicConfig(level=logging.DEBUG)
        self.rooms = set()
        self.edges = set()
    
    # ------------------------- Getters and setters -------------------------
        
    def addEdge(self, direction, (room1, room2)):
        '''Adds an Edge to this Graph, provided it doesn't already exist. Note: will override null Edges with non-null.'''
        #If there is already an edge going in this direction from room 1 to a non-null room,
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
                #Each room can only have one exit per direction, so we'll assume this is newer (and therefore more valid) information.
                #FIXME: This may have to be deprecated if rooms can have more than one exit per direction in future assignments.
                self.removeEdge(oldEdge)
        #Add the edge to both the graph and the room.
        self.edges.add(newEdge)
        room1.addEdge(newEdge)
            
    def removeEdge(self, edge):
        '''Removes an Edge from this Graph. Primarily useful for removing Edges pointing to null.'''
        room = edge.getRooms()[0]
        self.edges.remove(edge)
        room.removeEdge(edge)
        
                    
    def addRoom(self, room):
        '''Adds a new Room to this Graph and sets all its exits to null'''
        for myRoom in self.rooms:
            if myRoom.isEqual(room):
                return
        self.rooms.add(room)
        #New rooms are populated with edges going to null. It is the
        #responsibility of the GamePlayer class to update them later.
        for exit in room.getExits():
            self.addEdge(exit, (room, None))
        #Mark the room as visited
        room.visit()
        
    # ------------------------- More interesting stuff -------------------------
    
    def isNewRoom(self, room):
        '''Returns True if this room is not in the graph, False otherwise'''
        for thisRoom in self.rooms:
            if thisRoom.isEqual(room):
                return False
        return True
        
    def getEquivalentRoom(self, room):
        '''Looks through the room list to find a room equal to the given one and returns it. Returns None if there isn't one.'''
        for thisRoom in self.rooms:
            if thisRoom.isEqual(room):
                return thisRoom
        return None
            
        
    def getRoomList(self):
        '''Returns all the Rooms in this Graph in list format (generally easier to manage than sets)'''
        roomList = []
        for room in self.rooms:
            roomList.append(room)
        return roomList
        
    def getMinRoomIndex(self, roomList, distancesDict):
        '''DEPRECATED Returns the index in roomList of the Room with the minimum distance'''
        #FIXME: This has been deprecated and should probably be removed.
        #FIXME: There's a bug in here somewhere. It doesn't work right.
        minRoom = None
        dist = config.INFINITY
        for room in roomList:
            if distancesDict[room] <= dist:
                minRoom = room
                dist = distancesDict[room]
        return roomList.index(minRoom)
        
    def findBestPath(self, roomFrom):
        '''DEPRECATED Returns a collection of Rooms in a "best path" from roomFrom to the nearest null Room'''
        #FIXME: This doesn't actually work, and has been deprecated. It should probably be removed.
        #This will return a shortest path to anywhere from roomFrom (in dictionary format), if it exists in the graph (ignores unexplored paths)
        if roomFrom in self.rooms:
            dist = {}
            previous = {}
            for v in self.getRoomList():
                dist[v] = config.INFINITY
                previous[v] = None
            dist[roomFrom] = 0
            Q = self.getRoomList()
            logging.debug("ROOM LIST:" + str(self.getRoomList()))
            while not Q == []:
                u = Q.pop(self.getMinRoomIndex(Q, dist))
                logging.debug("u: " + str(u))
                for edge in u.getEdges():
                    if edge.getRooms()[1] is not None:
                        alt = dist[u] + edge.weight
                        if alt < dist[v]:
                            logging.debug("In the part that should be doing the write")
                            dist[v] = alt
                            previous[v] = u
            
            logging.debug("Best path determined as:")
            logging.debug(previous)
            logging.debug("")
            return previous
            


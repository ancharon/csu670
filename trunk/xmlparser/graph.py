#!/usr/bin/env python

from parser import *

class Edge(object):
    
    def __init__(self, direction, (node1=Node(), node2=Node())):
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
        
    def addEdge(self, direction, (node1, node2=Node())):
        #FIXME: If there is already an edge going in this direction from node 1 to a non-null node,
        # then don't add anything. Otherwise, add this new edge.
        self.edges.add(Edge(direction, (node1, node2)))
        
    def addRoom(self, room):
        self.rooms.add(room)
        self.addEdges(room)
        
#FIXME: This class should be in another file
#It should keep track of its last move, last room, and current room so that
# it can pass them to the graph as necessary.
class GamePlayer(object):
    
    def __init__(self):
        self.graph = Graph()
        self.currentRoom = None
        self.previousRoom = None
        self.lastMove = None
        
    def move(self, direction):
        #TODO: write move to stdout
        #do the move and save it to self.lastMove.
        myParser = gameparser.Xml2Obj()
        specname = os.path.join('xml', 'relaxng-hw5.rng')
        element = myParser.Parse(None, specname)
        if type(element) == Gameover:
            print element.outcome
        elif type(element) == Room:
            self.previousRoom = self.currentRoom
            self.currentRoom = element
        self.graph.addEdge(direction, (self.previousRoom, self.currentRoom))
        #FIXME: in future assignments, an exit might not exist 
        #in the opposite direction, so we should check for it before adding it
        self.graph.addEdge(oppositeDir, (self.currentRoom, self.previousRoom))
        self.graph.addEdges(self.currentRoom)
        
#FIXME: Unit tests needed
        
    
    
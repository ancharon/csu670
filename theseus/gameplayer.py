#!/usr/bin/env python
# encoding: utf-8
"""
gameplayer.py

Copyright (c) 2008 Nathan Palmer, Ethan Caldwell, David Fier. All rights reserved.
"""

import sys
import os
import unittest
import logging

import config
from graph import *
from gameparser import *

class OutputWriter(object):
    '''Used by the GamePlayer to write commands to stdout'''
    
    def __init__(self):
        self.output = sys.stdout
        
    def writeExit(self, dir):
        self.output.write("<exit>"+dir+"</exit>")
    
    # writeGrasp: Item -> None
    def writeGrasp(self, item):
        '''Writes a grasp command to self.output'''
        self.output.write("<grasp>"+item.toXML()+"</grasp>")
        
    def writeDrop(self):
        '''Writes a drop command to self.output'''
        self.output.write("<drop></drop>")
    
    # writeWrite assumes you are grasping paper
    # writeWrite: string -> None
    def writeWrite(self, text):
        '''Writes a write command to self.output'''
        self.output.write("<write>"+text+"</write>")
        
    def writeAssault(self):
        '''Writes an assault command to self.output'''
        self.output.write("<assault></assault>")

class GamePlayer(object):
    
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG,
                            filename='gameplayer.log',
                            filemode='w')
        logging.debug("Logger initialized.")
        self.graph = Graph()
        self.currentRoom = None
        self.previousRoom = None
        self.lastMove = None
        self.exitStrategy = []
        self.writer = OutputWriter()
        
    def writeMove(self, direction):
        '''Write a move to stdout.'''
        #sys.stderr.write("***************************Moving " + direction)
        logging.debug("Writing move:")
        logging.debug("<exit>" + direction + "</exit>")
        self.writer.writeExit(direction)
        #sys.stdout.write("<exit>" + direction + "</exit>" + os.linesep)
        #WHOOOOSH -- it's rude not to flush
        sys.stdout.flush()
        #sys.seat.down()
        
    def updateState(self, direction):
        '''Read a new element from stdin using the XML parser and update the state accordingly.'''
        element = self.getCurrentElement()
        
        if type(element) == Gameover:
            #Put the human-readable Gameover message to stderr so we know the outcome
            logging.debug("The game is over:")
            logging.debug(element.outcome)
            sys.exit(0)
        elif type(element) == Room:
            self.previousRoom = self.currentRoom
            self.currentRoom = element
            self.lastMove = direction
            logging.debug("I am now in a " + self.currentRoom.getPurpose())
            logging.debug("Its ID is: " + unicode(self.currentRoom))
            logging.debug("I moved " + unicode(direction) + " to get here.")
        else:
            logging.error("TypeError, Unhandled element type")
            raise TypeError, "Unhandled element type"
            
    def getCurrentElement(self):
        '''Returns either a Room or Gameover object, validated and parsed.'''
        myParser = Xml2Obj()
        return myParser.Parse(None, config.PATH_TO_INPUT_SPEC)
                
    def updateGraph(self):
        '''Adds new Rooms and Edges to the graph'''
        #When this method is done, we should be in a position to make an
        # informed decision about where to go next.
        
        #If this is a new room, we need to add it to the graph, as well as its
        # edges, all leading to null rooms since we don't know where they go.    
        if self.graph.isNewRoom(self.currentRoom):
            self.graph.addRoom(self.currentRoom)
        else:
            #This is an old room, we need a reference to it. Get one.
            self.currentRoom = self.graph.getEquivalentRoom(self.currentRoom)
            assert self.currentRoom is not None
            
        #Always add the edges for the exit we just came from. The graph will
        # just ignore it if you try to add something that already exists.
        if self.lastMove is not None:
            self.graph.addEdge(self.lastMove, (self.previousRoom, self.currentRoom))
            self.graph.addEdge(config.OPPOSITE_DIRS[self.lastMove], (self.currentRoom, self.previousRoom))
       
    def bfs(self, room):
        '''Returns a room with an unexplored exit, starting the search from the given room'''
        distances = {}
        previous = {}
        for thisRoom in self.graph.getRoomList():
            distances[thisRoom] = config.INFINITY
        distances[room] = 0
        previous[room] = None
        Q = [room]
        while Q is not []:
            thisRoom = Q.pop(0)
            for edge in thisRoom.getEdges():
                roomInQuestion = edge.getDestination()
                if roomInQuestion is None: #Haven't been there.
                    return (thisRoom, previous)
                elif distances[roomInQuestion] == config.INFINITY:
                    Q.append(roomInQuestion)
                    distances[roomInQuestion] = distances[thisRoom] + 1
                    previous[roomInQuestion] = thisRoom
        #This should never happen; if it does, wander lost in the castle forever
        logging.error("Error during search: No unexplored exits found.")
        raise self.SearchError, "No unexplored exits found in BFS"
        return (room, previous)
    
    #TODO: This needs to be returning arguments necessary for the next move, 
    # not just a direction. A move can be grasping or dropping an item, writing
    # on a piece of paper, or assaulting.
    def getNextMove(self):
        if not self.exitStrategy:
            for edge in self.currentRoom.getEdges():
                logging.debug("Found an exit in this direction: " + edge.getDirection())
                if not edge.isExplored():
                    logging.debug("Found a new exit in this direction: " + edge.getDirection())
                    return edge.getDirection()
                    
            #if we have run out of edges in this room we haven't seen before, we're 
            #going to ask the graph to give us a shortest path tree that will 
            #contain all rooms reachable from this room. we can then look 
            #through those rooms to find a path we haven't seen.
            #previousTree = self.graph.findBestPath(self.currentRoom)
            (nextRoom, previousTree) = self.bfs(self.currentRoom)
            logging.debug("previousTree:")
            logging.debug(unicode(previousTree))
            for item in previousTree:
                logging.debug(str(item))
                if type(item) is Room:
                    logging.debug(item.getPurpose())
            if nextRoom not in previousTree:
                #Well, crap. Go west, young man.
                logging.error("The room returned from the search was not found in the tree path.")
                raise self.SearchError, "The room returned from the search was not found in the tree path."
                return "west"
            else:
                logging.debug("Next room is in the previousTree")
                #nextRoom starts off as the destination room, the one with 
                # an unexplored exit returned by BFS. So we need to add it
                #first, then look up all the steps after that to build our 
                #exit strategy. Ugh.
                self.exitStrategy.insert(0, nextRoom)
                while previousTree[nextRoom] is not self.currentRoom:
                    logging.debug("Inside the while loop")
                    self.exitStrategy.insert(0, previousTree[nextRoom])
                    nextRoom = previousTree[nextRoom]
                
        # We have a plan. I love it when a plan comes together.
        logging.debug(os.linesep + "Exit strategy:")
        for item in self.exitStrategy:
            logging.debug(unicode(item.getPurpose()))
        nextRoomToMoveTo = self.exitStrategy.pop(0)
        logging.debug("nextRoomToMoveTo is: " + nextRoomToMoveTo.getPurpose())
        for edge in self.currentRoom.getEdges():
            logging.debug("edge destination is: " + edge.getDestination().getPurpose())
            if edge.getDestination() is nextRoomToMoveTo:
                return edge.getDirection()
        #OH NOES
        logging.error("Got through getNextMove without getting a direction.")
        logging.error("HALP WE R TRAPPED")
        return self.currentRoom.getAnExit()
 
    def takeTurns(self):
        '''Makes a move and updates the state to reflect the new situation.'''
        direction = None
        while(True):
            try:
                self.updateState(direction)
            except TypeError: #We got something other than a Room, Outside, or Gameover
                sys.exit(1)
            self.updateGraph()
            #TODO: getNextMove should not return a direction, but some
            # representation of a player action and its arguments. There
            # should be some internal state to deal with this as well so that
            # we know, for instance, what item we are grasping.
            direction = self.getNextMove()
            self.writeMove(direction)

    class SearchError(Exception):
       def __init__(self,value):
           self.parameter=value
       def __str__(self):
           return unicode(self.parameter)


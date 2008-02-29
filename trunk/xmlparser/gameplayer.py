#!/usr/bin/env python
# encoding: utf-8
"""
gameplayer.py

Created by Nathan Palmer on 2008-02-26.
Copyright (c) 2008 Nathan Palmer, Ethan Caldwell. All rights reserved.
"""

import sys
import os
import unittest
import logging

import config
from graph import *
from gameparser import *

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
        
    def writeMove(self, direction):
        '''Write a move to stdout.'''
        #FIXME: should be much more robust
        logging.debug("Writing move:")
        logging.debug("<exit>" + direction + "</exit>")
        sys.stdout.write("<exit>" + direction + "</exit>" + os.linesep)
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
            self.graph.addEdge(config.oppositeDirs[self.lastMove], (self.currentRoom, self.previousRoom))
       
    def bfs(self, room):
        '''Returns a room with an unexplored exit'''
        infinity = float("infinity")
        distances = {}
        for thisRoom in self.graph.getRoomList():
            distances[thisRoom] = infinity
        distances[room] = 0
        Q = [room]
        while Q is not []:
            u = Q.pop(0)
            for edge in u.getEdges():
                roomInQuestion = edge.getRooms()[1]
                if roomInQuestion is None: #Haven't been there.
                    return u
                elif distances[roomInQuestion] == infinity:
                    Q.append(roomInQuestion)
                    distances[roomInQuestion] = distances[u] + 1
        #This should never happen; if it does, wander lost in the castle forever
        logging.error("HALP WE R TRAPPED")
        return room
    
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
            shortestTree = self.graph.findBestPath(self.currentRoom)
            nextRoom = self.bfs(self.currentRoom)
            if nextRoom not in shortestTree:
                #Well, crap. Go west, young man.
                logging.error("HALP WE R TRAPPED AGAIN")
                return "west"
            else:
                logging.debug("Next room is in the shortestTree")
                #We're in luck!
                nextLookup = nextRoom
                if nextLookup is self.currentRoom:
                    for edge in self.currentRoom.getEdges():
                        logging.debug("Found an exit in this direction: " + edge.getDirection())
                        if not edge.isExplored():
                            return edge.getDirection()
                while nextLookup is not self.currentRoom:
                    logging.debug("Inserting nextLookup into exitStrategy")
                    logging.debug("nextLookup:")
                    logging.debug(str(nextLookup))
                    logging.debug(shortestTree)
                    logging.debug(str(shortestTree))
                    self.exitStrategy.insert(0, shortestTree[nextLookup])
                    nextLookup = shortestTree[nextLookup]
                
        # We have a plan. I love it when a plan comes together.
        nextRoomToMoveTo = self.exitStrategy.pop(0)
        for edge in nextRoomToMoveTo.getEdges():
            if edge.getRooms()[1] is nextRoomToMoveTo:
                return edge.getDirection()
        #OH NOES
        logging.error("Got through getNextMove without getting a direction.")
        return "west"
        
        
        #This is awesome. We should leave this alone.
        #return self.currentRoom.getAnExit()
 
    def takeTurns(self):
        '''Makes a move and updates the state to reflect the new situation.'''
        direction = None
        #This method should be run in a loop along with something to tell it
        # which direction to go each turn.
        while(True):
            self.updateState(direction)
            self.updateGraph()
            direction = self.getNextMove()
            self.writeMove(direction)

class GamePlayerTests(unittest.TestCase):
    
    def setUp(self):
        self.player = GamePlayer()
        self.infilePath = os.path.join("xml", "castleOneLoop.xml")
        self.infile = open(self.infilePath, 'r')
        sys.stdin = self.infile
        self.outfilePath = os.path.join("xml", "gameplayerTestOut.xml")
        self.outfile = open(self.outfilePath, 'w')
        sys.stdout = self.outfile
        
    def tearDown(self):
        self.infile.close()
        self.outfile.close()
        sys.stdin = sys.__stdin__
        sys.stdout = sys.__stdout__
        
    def getOutputLines(self):
        self.outfile.close()
        self.outfile = open(self.outfilePath, 'r')
        lines = self.outfile.readlines()
        self.outfile.close()
        self.outfile = open(self.outfilePath, 'w')
        return lines
        
    def testWriteMove(self):
        self.player.writeMove("east")
        lines = self.getOutputLines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].strip(), "<exit>east</exit>")

    def testGetCurrentElement(self):
        #This test will need to change if the input file changes.
        element = self.player.getCurrentElement()
        self.assertEqual(type(element), Room)
        #There's a second room, we don't bother testing it now but we have to
        # parse through it to get to the Gameover message.
        self.player.getCurrentElement()
        self.player.getCurrentElement()
        self.player.getCurrentElement()
        self.player.getCurrentElement()
        #This should be a Gameover.
        element2 = self.player.getCurrentElement()
        self.assertEqual(type(element2), Gameover)
        #Go back to the beginning of the file so we can use it again.
        self.infile.seek(0)
        
    def testUpdateState(self):
        #This simulates the first room of the castle
        self.player.updateState(None)
        self.assertEqual(self.player.previousRoom, None)
        self.assertEqual(type(self.player.currentRoom), Room)
        self.assertEqual(self.player.lastMove, None)
        room1 = self.player.currentRoom
        #Now the second...
        self.player.updateState("east")
        self.assertEqual(self.player.previousRoom, room1)
        self.assertEqual(type(self.player.currentRoom), Room)
        self.assertEqual(self.player.lastMove, "east")
        room2 = self.player.currentRoom
        #And a third.
        self.player.updateState("north")
        self.assertEqual(self.player.previousRoom, room2)
        self.assertEqual(type(self.player.currentRoom), Room)
        self.assertEqual(self.player.lastMove, "north")
        #Now reset the infile
        self.infile.seek(0)
        
    def testUpdateGraph(self):
        self.player.updateState(None)
        self.player.updateGraph()
        self.assert_(self.player.currentRoom in self.player.graph.getRoomList())
        room1 = self.player.currentRoom
        
        self.player.updateState("east")
        self.player.updateGraph()
        room2 = self.player.currentRoom
        self.assert_(room2 in self.player.graph.getRoomList())
        #The only edges we have now are:
        # 1. edges between room1 and room2
        # 2. edges between room1 and None
        # 3. edges between room2 and None
        counter = 0
        for edge in self.player.graph.edges:
            if None not in edge.getRooms():
                self.assert_(room1 in edge.getRooms())
                counter += 1
        #There should be exactly two edges connecting room1 and room2
        self.assertEqual(counter, 2)
        
        #Now we're just going to go around a loop.
        self.player.updateState("north")
        self.player.updateGraph()
        
        self.player.updateState("west")
        self.player.updateGraph()
        
        #We are now going back to the room we started in
        self.player.updateState("south")
        self.player.updateGraph()
        
        self.assert_(self.player.currentRoom == room1)
        

if __name__ == '__main__':
    unittest.main()
#!/usr/bin/env python
# encoding: utf-8
"""
gameplayer.py

Created by Nathan Palmer on 2008-02-26.
Copyright (c) 2008 Nathan Palmer. All rights reserved.
"""

import sys
import os
import unittest

import config
from graph import *
from gameparser import *

class GamePlayer(object):
    
    def __init__(self):
        self.graph = Graph()
        self.currentRoom = None
        self.previousRoom = None
        self.lastMove = None
        
    def writeMove(self, direction="north"):
        '''Write a move to stdout.'''
        
        #FIXME: should be much more robust
        sys.stdout.write("<exit>" + direction + "</exit>")
        
    def updateState(self):
        '''Read a new element from stdin using the XML parser and return it.'''
        element = self.getCurrentElement()
        
        if type(element) == Gameover:
            #Put the human-readable Gameover message to stderr so we know the outcome
            sys.stderr.write("The game is over." + os.linesep)
            sys.stderr.write(element.outcome)
            sys.exit(0)
        elif type(element) == Room:
            self.previousRoom = self.currentRoom
            self.currentRoom = element
            self.lastMove = direction
        else:
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
            
        #Always add the edges for the exit we just came from. The graph will
        # just ignore it if you try to add something that already exists.
        self.graph.addEdge(self.lastMove, (self.previousRoom, self.currentRoom))
        self.graph.addEdge(config.oppositeDirs[self.lastMove], (self.currentRoom, self.previousRoom))
                
    def getNextMove(self):
        return self.currentRoom.getAnExit()
 
    def takeTurns(self):
        '''Makes a move and updates the state to reflect the new situation.'''
        #This method should be run in a loop along with something to tell it
        # which direction to go each turn.
        while(True):
            self.updateState()
            self.updateGraph()
            direction = self.getNextMove()
            self.writeMove(direction)

class GameplayerTests(unittest.TestCase):
    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()
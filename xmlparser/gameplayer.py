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

from graph import *
from gameparser import *

class GamePlayer(object):
    
    def __init__(self):
        self.graph = Graph()
        self.currentRoom = None
        self.previousRoom = None
        self.lastMove = None
        
    def move(self, direction):
        '''Write a move to stdout and read a new element from stdin. Update the graph status to reflect the new state.'''
        #When this method is done, we should be in a position to make an
        # informed decision about where to go next.
        
        #TODO: write move to stdout
        #do the move and save it to self.lastMove.
        element = self.getCurrentElement()
        
        if type(element) == Gameover:
            #Put the human-readable Gameover message to stderr so we know the outcome
            sys.stderr.write("The game is over." + os.linesep)
            sys.stderr.write(element.outcome)
            sys.exit()
        elif type(element) == Room:
            self.previousRoom = self.currentRoom
            self.currentRoom = element
        
        #If this is a new room, we need to add it to the graph, as well as its
        # edges, all leading to null rooms.    
        if self.isNewRoom(self.currentRoom):
            self.graph.addRoom(self.currentRoom)
            self.graph.addEdge(self.lastMove, (self.previousRoom, self.currentRoom))
            #FIXME: in future assignments, an exit might not exist 
            #in the opposite direction, so we should check for it before adding it.
            #FIXME: We need a dictionary of opposite directions.
            self.graph.addEdge(opposite[self.lastMove], (self.currentRoom, self.previousRoom))
        #If this is not a new room, update the edges associated with our last
        # move. This is held in self.lastMove.    
        else:
            self.graph.updateEdge(self.lastMove, (self.previousRoom, nullRoom), )
            
        #Add edges leading to a null room for any remaining exits
        self.graph.addEdges(self.currentRoom)
        
    def isNewRoom(room):
        pass
        
    def getCurrentElement(self):
        '''Returns either a Room or Gameover object, parsed and verified.'''
        myParser = gameparser.Xml2Obj()
        #FIXME: specname should be declared in a config file
        specname = os.path.join('xml', 'relaxng-hw5.rng')
        return myParser.Parse(None, specname)


class GameplayerTests(unittest.TestCase):
    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()
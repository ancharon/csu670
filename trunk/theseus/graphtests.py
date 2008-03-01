#!/usr/bin/env python
# encoding: utf-8
"""
graphtests.py

Copyright (c) 2008 Nathan Palmer, Ethan Caldwell, David Fier. All rights reserved.
"""


import sys, os
import unittest
from graph import *
from gameplayer import *

class RoomTests(unittest.TestCase):
    '''Tests for the Room class'''

    def setUp(self):
        self.player = GamePlayer()
        self.infilePath = os.path.join("xml", "castleOneLoop.xml")
        self.infile = open(self.infilePath, 'r')
        sys.stdin = self.infile
        
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
        
        #These two test rooms may have to change if the infile changes
        self.room3 = self.player.getCurrentElement()
        self.room4 = self.player.getCurrentElement()

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
        
        #Test rooms initialized through XML work as well
        result = self.room3.isEqual(self.room4)
        self.assertEqual(result, False)

class GameOverTests(unittest.TestCase):
    def setUp(self):
        self.gameover = Gameover()
        
    #Test if setOutcome has assigned an outcome.  Should only be the case on Game Over.  Result true if game is over.
    def testIsGameOver(self):
        self.gameover.setOutcome("Game Over")
        result = (self.gameover.outcome is not "")
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
        
class GraphTests(unittest.TestCase):
    def setUp(self):
        self.player = GamePlayer()
        self.infilePath = os.path.join("xml", "castleOneLoop.xml")
        self.infile = open(self.infilePath, 'r')
        sys.stdin = self.infile
        
        self.graph = Graph()
        
        #These may need to change if the infile changes
        self.room1 = self.player.getCurrentElement()
        self.room2 = self.player.getCurrentElement()
        self.room3 = self.player.getCurrentElement()
        self.room4 = self.player.getCurrentElement()
        self.room5 = self.player.getCurrentElement()
        
    def testAddRooms(self):
        self.assertEqual(len(self.graph.rooms) == 0, True)
        
        self.graph.addRoom(self.room1)
        self.assertEqual(self.graph.rooms is not None, True)
        self.graph.addRoom(self.room2)
        self.graph.addRoom(self.room3)
       
        self.assertEqual(len(self.graph.rooms) == 3, True)
        self.roomList = self.graph.getRoomList()
        self.assertEqual(len(self.roomList) == 3, True)
        for room in self.roomList:
            self.assert_(room is not None)
        
        #self.room1 == self.room5 for this file
        self.assert_(not self.graph.isNewRoom(self.room5))
        self.graph.addRoom(self.room5)
        self.assert_(not self.graph.isNewRoom(self.room5))
        
        self.assert_(self.graph.isNewRoom(self.room4))
        self.graph.addRoom(self.room4)
        self.assert_(not self.graph.isNewRoom(self.room4))
        
        self.assert_(len(self.graph.rooms) == 4)
        
if __name__ == "__main__":
    unittest.main()
        
    
    
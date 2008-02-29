#!/usr/bin/env python

import sys, os
import unittest

from gameplayer import *

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
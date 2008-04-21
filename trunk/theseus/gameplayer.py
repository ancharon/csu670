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
import copy

import config
from graph import *
from gameparser import *

class OutputWriter(object):
    '''Used by the GamePlayer to write commands to stdout '''
    
    #    <!-- Relax NG specification of output messages -->

    # <choice xmlns="http://relaxng.org/ns/structure/1.0"
            # datatypeLibrary="http://www.w3.org/2001/XMLSchema-datatypes">
      # <element name="stop">
        # <empty/>
      # </element>
      # <element name="enter">
        # <empty/>
      # </element>
      # <element name="exit">
        # <choice>
          # <value>up</value>
          # <value>down</value>
          # <value>north</value>
          # <value>east</value>
          # <value>south</value>
          # <value>west</value>
        # </choice>
      # </element>
      # <element name="grasp">
        # <choice>
          # <element name="frog">
            # <empty/>
          # </element>
          # <element name="paper">
            # <text/>
          # </element>
          # <element name="treasure">
            # <attribute name="style">
              # <text/>
            # </attribute>
            # <data type="int"/>
          # </element>
          # <element name="shield">
            # <attribute name="style">
              # <text/>
            # </attribute>
            # <data type="int"/>
          # </element>
          # <element name="weapon">
            # <attribute name="style">
              # <text/>
            # </attribute>
            # <data type="int"/>
          # </element>
        # </choice>
      # </element>
      # <element name="drop">
        # <empty/>
      # </element>
      # <element name="write">
        # <text/>
      # </element>
      # <element name="assault">
        # <empty/>
      # </element>
    # </choice>
    
    def __init__(self):
        self.output = sys.stdout
        
    def write(self, move):
        if isinstance(move, Enter):
            self.writeEnter()
        elif isinstance(move, Stop):
            self.writeStop()
        elif isinstance(move, Exit):
            self.writeExit(move)
        elif isinstance(move, Grasp):
            self.writeGrasp(move)
        elif isinstance(move, Drop):
            self.writeDrop()
        elif isinstance(move, Write):
            self.writeWrite(move)
        elif isinstance(move, Assault):
            self.writeAssault()
        else:
            logging.error("Invalid move: "+str(move))
            raise InvalidMoveError, "Invalid move: "+str(move)
        
        #WHOOOOSH -- it's rude not to flush
        sys.stdout.flush()
        #sys.seat.down()
        return
            
        
    def writeEnter(self):
        '''Writes an enter command to self.output'''
        sys.stderr.write("***************************Entering")
        logging.debug("Entering")
        self.output.write("<enter></enter>")
        
    def writeStop(self):
        '''Writes a stop command to self.output'''
        sys.stderr.write("***************************Stopping")
        logging.debug("Stopping")
        self.output.write("<stop></stop>")
        
    #writeExit: Exit -> None    
    def writeExit(self, exit):
        sys.stderr.write("***************************Moving " + exit.direction)
        logging.debug("Writing move:" + exit.direction)
        self.output.write("<exit>"+exit.direction+"</exit>")
    
    # writeGrasp: Item -> None
    def writeGrasp(self, grasp):
        '''Writes a grasp command to self.output'''
        sys.stderr.write("***************************Grasping " + grasp.item.toString())
        logging.debug("Grasping " + grasp.item.toString())
        self.output.write("<grasp>"+grasp.item.toXML()+"</grasp>")
        
    def writeDrop(self):
        '''Writes a drop command to self.output'''
        sys.stderr.write("***************************Dropping")
        logging.debug("Dropping")
        self.output.write("<drop></drop>")
    
    # writeWrite assumes you are grasping paper
    # writeWrite: string -> None
    def writeWrite(self, write):
        '''Writes a write command to self.output'''
        sys.stderr.write("***************************Writing " + write.text)
        logging.debug("Writing " + write.text)
        self.output.write("<write>"+write.text+"</write>")
        
    def writeAssault(self):
        '''Writes an assault command to self.output'''
        sys.stderr.write("***************************Assaulting")
        logging.debug("Assaulting")
        self.output.write("<assault></assault>")
        
    class InvalidMoveError(Exception):
       def __init__(self,value):
           self.parameter=value
       def __str__(self):
           return unicode(self.parameter)
        
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
        self.lastExit = None
        self.exitStrategy = []
        self.writer = OutputWriter()
        #If we think the frog has been found, this gets set to True. It may
        # be a lie if somebody is a dick and goes around writing the secret
        #code on pieces of paper.
        self.frogFound = False
        
    def writeMove(self, move):
        '''Write a move to stdout.'''
        self.writer.write(move)
    
    def updateState(self, move):
        '''Read a new element from stdin using the XML parser and update the state accordingly.'''
        sys.stderr.write("We are in updateState.\n")
        element = self.getCurrentElement()
        sys.stderr.write("Got element: " + str(element) + "\n")
        if move is not None:
            sys.stderr.write("Got move: "+str(move))
        else:
            sys.stderr.write("Got no fancy moves")
        
        if type(element) == Gameover:
            #Put the human-readable Gameover message to stderr so we know the outcome
            logging.debug("The game is over:")
            logging.debug(element.outcome)
            sys.exit(0)
        elif type(element) == Outside:
            #We basically need to start over from the beginning, unless by
            # sheer luck we end up in a room we already know about when 
            # we re-enter the castle.
            logging.debug("Went outside.")
            self.currentRoom.setHasOutsideExit(True)
            self.previousRoom = self.currentRoom
            self.currentRoom = Outside()
            self.lastMove = move
        elif type(element) == Room:
            if move is None or isinstance(move, Exit):
                self.handleExit(move, element)
            else:
                self.handleNonExit(move, element)
        else:
            logging.error("TypeError, Unhandled element type")
            raise TypeError, "Unhandled element type"
    
    def handleNonExit(self, move, element):
        '''Handle updating the state for non-exit moves.'''
        self.lastMove = move
        logging.debug("I just took the following action: "+str(move))
    
    def handleExit(self, move, element):
        '''Handle updating the state for exit moves.'''
        self.previousRoom = self.currentRoom
        self.currentRoom = element
        self.lastMove = move
        logging.debug("I am now in a " + self.currentRoom.getPurpose())
        logging.debug("Its ID is: " + unicode(self.currentRoom))
        if move is not None:
            logging.debug("I moved " + move.direction + " to get here.")
        
    def getCurrentElement(self):
        '''Returns either a Room, Outside, or Gameover object, validated and parsed.'''
        myParser = Xml2Obj()
        return myParser.Parse(None, config.PATH_TO_INPUT_SPEC)
                
    def updateGraph(self):
        '''Adds new Rooms and Edges to the graph'''
        #When this method is done, we should be in a position to make an
        # informed decision about where to go next.
        
        #If this is a new room, we need to add it to the graph, as well as its
        # edges, all leading to null rooms since we don't know where they go.
        #The line between Rooms and Outsides is fuzzy. We might be getting
        # outsides here as well as Rooms. Deal with it.
        if self.graph.isNewRoom(self.currentRoom):
            self.graph.addRoom(self.currentRoom)
        else:
            #This is an old room, we need a reference to it. Get one.
            self.currentRoom = self.graph.getEquivalentRoom(self.currentRoom)
            assert self.currentRoom is not None
            
        #Always add the edges for the exit we just came from. The graph will
        # just ignore it if you try to add something that already exists.
        if self.lastMove is not None:
            if isinstance(self.currentRoom, Outside):
                self.graph.addEdge(self.lastMove, (self.previousRoom, self.currentRoom))
                #If we go outside and come back in, everything we know is a lie.
                #We are starting over from scratch until we find a Room we recognize.
                self.previousRoom = None
                self.lastMove = None
            else:
                self.graph.addEdge(self.lastMove, (self.previousRoom, self.currentRoom))
                self.graph.addEdge(Exit(config.OPPOSITE_DIRS[self.lastMove.direction]), (self.currentRoom, self.previousRoom))
       
    def bfs(self, room):
        '''Returns a room with an unexplored exit, starting the search from the given room'''
        #TODO: fix this to deal with:
        # 1. Finding Outsides if we can't find null rooms
        # 2. Finding Outsides if the frog has been found
        distances = {}
        previous = {}
        firstNullRoom = None
        previousFirstNullRoom = {}
        for thisRoom in self.graph.getRoomList():
            distances[thisRoom] = config.INFINITY
        distances[room] = 0
        previous[room] = None
        Q = [room]
        while Q is not []:
            thisRoom = Q.pop(0)
            #This is a Room, not an Outside
            if isinstance(thisRoom, Room):
                # If this room we're looking at has an outside exit somewhere and the frog has been found
                # then we can just return this room and the path to it.
                if self.frogFound and thisRoom.getHasOutsideExit():
                    return (thisRoom, previous)
                for edge in thisRoom.getEdges():
                    roomInQuestion = edge.getDestination()
                    if self.frogFound:
                        #Find an Outside. If we can't find an outside, find an
                        # unexplored exit.
                        if roomInQuestion is None:
                            # We only want to store the closest null room, so only do this once.
                            if firstNullRoom is None:
                                firstNullRoom = copy.copy(thisRoom)
                                previousFirstNullRoom = copy.copy(previous)
                        elif isinstance(roomInQuestion, Outside):
                            return (thisRoom, previous)
                        elif distances[roomInQuestion] == config.INFINITY:
                            Q.append(roomInQuestion)
                            distances[roomInQuestion] = distances[thisRoom] + 1
                            previous[roomInQuestion] = thisRoom
                    else:
                        if roomInQuestion is None: #Haven't been there.
                            return (thisRoom, previous)
                        # We're not looking for an Outside at this point, so let's just ignore this for now.
                        elif isinstance(roomInQuestion, Outside):
                            pass
                        elif distances[roomInQuestion] == config.INFINITY:
                            Q.append(roomInQuestion)
                            distances[roomInQuestion] = distances[thisRoom] + 1
                            previous[roomInQuestion] = thisRoom
            else: #This is an Outside, not a Room
                # Outside objects should never be added to the queue
                logging.error("An Outside was added to the bfs queue")
                raise self.SearchError, "An Outside was added to the bfs queue"
        
        # If we got through the bfs and didn't return, it's possible that these condition was met and is not an error:
        # 1. self.frogFound is True
        # 2. firstNullRoom was set to a room with a null exit
        # 3. previousFirstNullRoom was set to the path to the aforementioned room
        # If these three conditions were met and these variables were set correctly, that means we didn't find a path to the outside
        # but we found a path to a null room. Good enough, let's follow it.
        if firstNullRoom is not None and previousFirstNullRoom is not None:
            assert(self.frogFound)
            return (firstNullRoom, previousFirstNullRoom)
        # If the three conditions above were not met, then we got stuck someplace with no unexplored rooms or exits to the Outside.
        # That's pretty bad, let's throw an error.
        else:
            #This should never happen; if it does, wander lost in the castle forever
            logging.error("Error during search: No unexplored exits found.")
            raise self.SearchError, "No unexplored exits found in BFS"
            return (room, previous)
            
    def checkThisRoomForNewExits(self):
        for edge in self.currentRoom.getEdges():
            logging.debug("Found an exit in this direction: " + edge.getDirection())
            if not edge.isExplored():
                logging.debug("Found a new exit in this direction: " + edge.getDirection())
                return Exit(edge.getDirection())
        return None
    
    #TODO: This needs to be returning arguments necessary for the next move, 
    # not just a direction. A move can be grasping or dropping an item, writing
    # on a piece of paper, or assaulting.
    def getNextMove(self):
        if self.frogFound:
            logging.debug("getNextMove thinks the frog is found.")
        else:
            if isinstance(self.currentRoom, Outside):
                #We're outside and the game's not over, go back in.
                sys.stderr.write("We made it out alive!\n")
                sys.exit(0)
            else:
                for item in self.currentRoom.items:
                    logging.debug("Item in current room: " + item.toString())
                    if isinstance(item, Frog):
                        logging.debug("THE FROG! GET THE FROG! FROGGYFROGFROG")
                        return Grasp(item)
                        
                logging.debug("No frog here :(")
    
                if not self.exitStrategy:
                    temp = self.checkThisRoomForNewExits()
                    if temp is not None:
                        return temp
                            
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
                        logging.error("The room returned from the search was not found in the tree path.")
                        raise self.SearchError, "The room returned from the search was not found in the tree path."
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
                        return Exit(edge.getDirection())
                #OH NOES
                logging.error("Got through getNextMove without getting a direction.")
                logging.error("HALP WE R TRAPPED")
                return Exit(self.currentRoom.getAnExit())
 
    def handleThisMove(self, move):
        if isinstance(move, Exit):
            pass
        elif isinstance(move, Grasp):
            self.currentRoom.removeItem(move.item)
        else:
            pass
    
    def takeTurns(self):
        '''Makes a move and updates the state to reflect the new situation.'''
        #TODO: Handle differences between "exit" moves and other moves.
        move = None
        while(True):
            self.updateState(move)
            if self.lastMove is None or isinstance(self.lastMove, Exit):
                logging.debug("Updating graph")
                self.updateGraph()
            #TODO: getNextMove should not return a direction, but some
            # representation of a player action and its arguments. There
            # should be some internal state to deal with this as well so that
            # we know, for instance, what item we are grasping.
            move = self.getNextMove()
            self.handleThisMove(move)
            self.writeMove(move)

    class SearchError(Exception):
       def __init__(self,value):
           self.parameter=value
       def __str__(self):
           return unicode(self.parameter)


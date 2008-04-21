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
        #sys.stderr.write("***************************Entering" + os.linesep)
        logging.debug("Entering")
        self.output.write("<enter></enter>")
        
    def writeStop(self):
        '''Writes a stop command to self.output'''
        #sys.stderr.write("***************************Stopping" + os.linesep)
        logging.debug("Stopping")
        self.output.write("<stop></stop>")
        
    #writeExit: Exit -> None    
    def writeExit(self, exit):
        #sys.stderr.write("***************************Moving " + exit.direction + os.linesep)
        logging.debug("Writing move:" + exit.direction)
        self.output.write("<exit>"+exit.direction+"</exit>")
    
    # writeGrasp: Item -> None
    def writeGrasp(self, grasp):
        '''Writes a grasp command to self.output'''
        #sys.stderr.write("***************************Grasping " + grasp.item.toString() + os.linesep)
        logging.debug("Grasping " + grasp.item.toString())
        self.output.write("<grasp>"+grasp.item.toXML()+"</grasp>")
        
    def writeDrop(self):
        '''Writes a drop command to self.output'''
        #sys.stderr.write("***************************Dropping" + os.linesep)
        logging.debug("Dropping")
        self.output.write("<drop></drop>")
    
    # writeWrite assumes you are grasping paper
    # writeWrite: string -> None
    def writeWrite(self, write):
        '''Writes a write command to self.output'''
        #sys.stderr.write("***************************Writing " + write.text + os.linesep)
        logging.debug("Writing " + write.text)
        self.output.write("<write>"+write.text+"</write>")
        
    def writeAssault(self):
        '''Writes an assault command to self.output'''
        #sys.stderr.write("***************************Assaulting" + os.linesep)
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
        # TODO: We're not using this for anything now, though we would be
        # if we had had more time to work on the assignment.
        self.frogFound = False
        
    def writeMove(self, move):
        '''Write a move to stdout.'''
        self.writer.write(move)
    
    def updateState(self, move):
        '''Read a new element from stdin using the XML parser and update the state accordingly.'''
        #sys.stderr.write("We are in updateState.\n")
        element = self.getCurrentElement()
        #sys.stderr.write("Got element: " + str(element) + "\n")
        #if move is not None:
        #    sys.stderr.write("Got move: "+str(move) + os.linesep)
        #else:
        #    sys.stderr.write("Got no fancy moves" + os.linesep)
        
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
            logging.debug("I am now in a " + element.getPurpose())
            logging.debug("Its ID is: " + unicode(element))
            if move is None or isinstance(move, Exit):
                self.handleExit(move, element)
            else:
                self.handleNonExit(move, element)
        else:
            logging.error("TypeError, Unhandled element type")
            raise TypeError, "Unhandled element type"
    
    def handleNonExit(self, move, element):
        '''Handle updating the state for non-exit moves.'''
        logging.debug("I just took the following action: "+str(move))
        if isinstance(move, Enter):
            self.lastMove = None
            self.previousRoom = None
            self.currentRoom = element
            self.currentRoom.setHasOutsideExit(True)
        else:
            self.lastMove = move
    
    def handleExit(self, move, element):
        '''Handle updating the state for exit moves.'''
        self.previousRoom = self.currentRoom
        self.currentRoom = element
        self.lastMove = move
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
            logging.debug("Got a new room: " + str(self.currentRoom))
            self.graph.addRoom(self.currentRoom)
        else:
            #This is an old room, we need a reference to it. Get one.
            logging.debug("Got an old room: " + str(self.currentRoom))
            self.currentRoom = self.graph.getEquivalentRoom(self.currentRoom)
            logging.debug("Old room set to equivalent room: " + str(self.currentRoom))
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
        distances = {}
        previous = {}
        
        firstNullRoom = None
        #previousFirstNullRoom = {}
        
        firstOutsideRoom = None
        #previousFirstOutsideRoom = {}
        
        for thisRoom in self.graph.getRoomList():
            distances[thisRoom] = config.INFINITY
        distances[room] = 0
        previous[room] = None
        Q = [room]
        
        while Q != []:
            #sys.stderr.write("The queue is: " + str(Q) + os.linesep)
            thisRoom = Q.pop(0)
            #This is a Room, not an Outside
            if isinstance(thisRoom, Room):
                # If this room we're looking at has an outside exit somewhere and the frog has been found
                # then we can just return this room and the path to it.
                #if self.frogFound and thisRoom.getHasOutsideExit():
                #    logging.debug("Frog found and this room has an outside exit")
                #    return (thisRoom, previous)
                for edge in thisRoom.getEdges():
                    roomInQuestion = edge.getDestination()
                    # TODO: This logic is meant to be used if we have a different
                    # exploration plan depending on whether we think the frog has
                    # been found or not. This leads to a lot of complex situations
                    # that we don't want/have time to deal with for this assignment.
                    
                    #if self.frogFound:
                        #Find an Outside. If we can't find an outside, find an
                        # unexplored exit.
                    #    if roomInQuestion is None:
                            # We only want to store the closest null room, so only do this once.
                    #        if firstNullRoom is None:
                    #            logging.debug("Setting firstNullRoom to: " + str(thisRoom))
                    #            firstNullRoom = thisRoom
                                #previousFirstNullRoom = copy.copy(previous)
                    #    elif isinstance(roomInQuestion, Outside):
                    #        return (thisRoom, previous)
                    #    elif distances[roomInQuestion] == config.INFINITY:
                    #        Q.append(roomInQuestion)
                    #        distances[roomInQuestion] = distances[thisRoom] + 1
                    #        previous[roomInQuestion] = thisRoom
                    #else:
                    if roomInQuestion is None: #Haven't been there.
                        return (thisRoom, previous)
                    # We're not looking for an Outside at this point, so let's just ignore this for now.
                    elif isinstance(roomInQuestion, Outside):
                        if firstOutsideRoom is None:
                            firstOutsideRoom = thisRoom
                    elif distances[roomInQuestion] == config.INFINITY:
                        Q.append(roomInQuestion)
                        distances[roomInQuestion] = distances[thisRoom] + 1
                        previous[roomInQuestion] = thisRoom
            else: #This is an Outside, not a Room
                # Outside objects should never be added to the queue
                logging.error("An Outside was added to the bfs queue")
                raise self.SearchError, "An Outside was added to the bfs queue"
                
        # It's possible to get in a situation where we enter a dead-end room we have already been to,
        # so bfs won't find any new exits to explore. In this case, we need to go back outside and try again.
        if firstOutsideRoom is not None: #and previousFirstOutsideRoom is not None:
            #assert(not self.frogFound)
            logging.debug("frogFound is False, we have a firstOutsideRoom and its previous tree to return")
            return (firstOutsideRoom, previous)
        # If this condition was not met, then we got stuck someplace with no unexplored rooms or exits to the Outside.
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
    
    #FIXME: This would have been our plan for dealing with Items if we had had more time to implement the program
    # It's pseudocode, so hopefully it's fairly readable.
    
    #The plan:
    #   If the frog has not been found:
    #       If the frog is in this room:
    #           If we are carrying paper:
    #               If the paper says "banana":
    #                   Drop()
    #               Else:
    #                   Write(banana)
    #           Else If paper is in this room and paper.text is not "banana":
    #               If we are carrying something:
    #                   Drop()
    #               Else:
    #                   Grasp(paper)
    #           Else: [the frog is here but there's no paper, or there is paper but it has "banana" written on it]
    #               If we are carrying something:
    #                   Drop()
    #               Else:
    #                   set Frog found
    #                   Grasp(frog)
    #       Else: [Frog is not in this room]
    #           If paper is in room and paper.text is "banana":
    #               set Frog found
    #               Exit([use exit strategy])
    #           If we are carrying paper:
    #               Exit([use explore strategy])
    #           Else If paper is in this room:
    #               If we are carrying something:
    #                   Drop()
    #               Else:
    #                   Grasp(paper)
    #           Else If we are carrying treasure:
    #               If treasure is in this room:
    #                   If the treasure in the room has a higher value than ours:
    #                       Drop()
    #                   Else:
    #                       Exit([use explore strategy])
    #               Else: [no treasure]
    #                   Exit([use explore strategy])
    #           Else If treasure is in this room:
    #               Grasp([highest value treasure in the room])
    #   Else: [We think the frog has been found]
    #       If we are carrying the frog:
    #           If paper is in this room and paper.text is not "banana": [we only drop the frog to write on paper]
    #               Drop()
    #           Else:
    #               Exit([use exit strategy])
    #       Else: [either we put the Frog down or someone else found it]
    #           If we are carrying paper:
    #               If the paper says "banana":
    #                   Drop()
    #               Else:
    #                   Write(banana)
    #           Else If paper is in this room and paper.text is not "banana":
    #               If we are carrying something:
    #                   Drop()
    #               Else:
    #                   Grasp(paper)
    #           Else If Frog is in this room: [the frog is here but there's no paper, or there is paper but it already has "banana" written on it]
    #               If we are carrying something:
    #                   Drop()
    #               Else:
    #                   Grasp(frog)
    #           Else: [The frog is not here, we aren't carrying any paper, any paper in the room already has "banana" written on it]
    #               If treasure is in this room:
    #                   If we are carrying treasure:
    #                       If a treasure in the room has higher value than our treasure:
    #                           Drop()
    #                       Else:
    #                           Exit([use exit strategy])
    #                   Else: [we're not carrying treasure]
    #                       If we are carrying something:
    #                           Drop()
    #                       Else:
    #                           Grasp([highest value treasure])
    #               Else: [no treasure in this room]
    #                   Exit([use exit strategy])

    
    def getNextMove(self):
        '''Returns the next move we should make'''
        if isinstance(self.currentRoom, Outside):
            #We're outside and the game's not over, go back in.
            #sys.stderr.write("We made it out alive!\n")
            return Enter()
        else:
            for item in self.currentRoom.items:
                logging.debug("Item in current room: " + item.toString())
                if isinstance(item, Frog):
                    logging.debug("THE FROG! GET THE FROG! FROGGYFROGFROG")
                    self.frogFound = True
                    return Grasp(item)

            if not self.exitStrategy:
                temp = self.checkThisRoomForNewExits()
                if temp is not None:
                    return temp
                        
                #if we have run out of edges in this room we haven't seen before, we're 
                #going to ask the graph to give us a shortest path tree that will 
                #contain all rooms reachable from this room. we can then look 
                #through those rooms to find a path we haven't seen or to the outside.
                #previousTree = self.graph.findBestPath(self.currentRoom)
                (nextRoom, previousTree) = self.bfs(self.currentRoom)
                logging.debug("nextRoom:")
                logging.debug(unicode(nextRoom))
                logging.debug(nextRoom.getPurpose())
                logging.debug("previousTree:")
                logging.debug(unicode(previousTree))
                
                for item in previousTree:
                    logging.debug(str(item))
                    if type(item) is Room:
                        logging.debug(item.getPurpose())
                
                #This will only fire if we end up in a completely explored segment with the closest
                # path to the outside from the current room.
                # In this case, we should find not a null exit, but an exit to the outside from this room.
                if nextRoom.isEqual(self.currentRoom):
                    for edge in self.currentRoom.getEdges():
                        if isinstance(edge.getDestination(), Outside):
                            logging.debug("Returning an exit to the outside in this direction: " + edge.getDirection())
                            return Exit(edge.getDirection())
                
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
                        self.exitStrategy.insert(0, previousTree[nextRoom])
                        nextRoom = previousTree[nextRoom]
                    
            # We have a plan. I love it when a plan comes together.
            logging.debug(os.linesep + "Exit strategy:")
            for item in self.exitStrategy:
                logging.debug(item.getPurpose())
            nextRoomToMoveTo = self.exitStrategy.pop(0)
            logging.debug("nextRoomToMoveTo is: " + nextRoomToMoveTo.getPurpose())
            for edge in self.currentRoom.getEdges():
                if isinstance(edge.getDestination(), Room):
                    logging.debug("edge destination is: " + edge.getDestination().getPurpose())
                elif isinstance(edge.getDestination(), Outside):
                    logging.debug("edge destination is: Outside")
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
        move = None
        while(True):
            self.updateState(move)
            if self.lastMove is None or isinstance(self.lastMove, Exit):
                logging.debug("Updating graph")
                self.updateGraph()
            move = self.getNextMove()
            self.handleThisMove(move)
            self.writeMove(move)

    class SearchError(Exception):
       def __init__(self,value):
           self.parameter=value
       def __str__(self):
           return unicode(self.parameter)


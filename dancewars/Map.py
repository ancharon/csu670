import sys, os, pygame, time
from pygame.locals import *

from Constants import *
import Unit, Announcer

## Exceptions
class NoUnitAtPositionError(Exception):
    """Raised when a unit is expected at a position, but no unit is there"""
    def __init(self, value):
        self.value = value
    def __str__(self):
        return "No unit at position "+str(value)
    
class NoBaseAtPositionError(Exception):
    """Raised when a base is expected at a position, but no base is there"""
    def __init(self, value):
        self.value = value
    def __str__(self):
        return "No base at position "+str(value)
    
class InvalidCoordinatesError(Exception):
    """Raised when we receive a set of coordinates outside the bounds of the map"""
    def __init(self, value):
        self.value = value
    def __str__(self):
        return "No unit at position "+str(value)

class Map(object):
    """Class for Maps"""
    def __init__(self, terrain, teams, teamAffiliations):
        self.width = len(terrain[0])
        self.height = len(terrain)
        print "Width: "+str(self.width)
        print "Height: " + str(self.height)
        self.terrain = TerrainGroup()
        self.terrainGrid = []
        x = 0
        y = 0
        #Parse through terrain (a list of lists of ints) and
        #create self.terrain, a sprite group of TerrainTiles.
        #Also create self.terrainGrid, a list of lists of TerrainTiles
        teamCounter = 0
        for row in terrain:
            currentRow = []
            for tile in row:
                thisTerrain = TERRAIN_LOOKUP[tile]((x, y))
                if thisTerrain.team:
                    thisTerrain.team = teamAffiliations[teamCounter]
                    thisTerrain.setImage(TEAM_BASE_IMAGES[thisTerrain.team.color])
                    teamCounter += 1
                self.terrain.add(thisTerrain)
                currentRow.append(thisTerrain)
                x += 1
            self.terrainGrid.append(currentRow)
            x = 0
            y += 1
        self.units = Unit.UnitGroup() #all the units on the map
        self.overlayImage = None
        self.overlayList = OverlayGroup()
        self.teams = teams #List of teams, in the proper turn order
        self.turnCounter = 0
        self.currentTeam = self.teams[self.turnCounter]
        self.dayCounter = 1
        self.attackMode = False
        self.announcers = Announcer.AnnouncerGroup(self, 1.2)
        self.turnStartTime = None
        
    def setAttackMode(self):
        self.attackMode = True
    
    def endAttackMode(self):
        self.attackMode = False
    
    def getTileAt(self, (x, y)):
        """Takes an (x, y) position and returns the tile at that position"""
        #print "Getting tile at ("+str(x)+", "+str(y)+")"
        return self.terrainGrid[y][x]
        
    def changeTurns(self):
        """Ends a turn and starts the next"""
        self.turnStartTime = time.time()
        self.turnCounter += 1
        if self.turnCounter == len(self.teams):
            self.turnCounter = 0
            self.dayCounter += 1
        self.currentTeam = self.teams[self.turnCounter]
        #Tell all the units that a new turn is starting, 
        #  and set their new legal moves 
        for unit in self.units:
            unit.newTurn()
            unit.setLegalMoves(self.getLegalMoves(unit))
            self.announcers.add(Announcer.Announcer(self.currentTeam.name))
            
    def removeAnnouncements(self):
        self.announcers.empty()    
    
#    def showWhoseTurn(self, team):
#        teamName = TEAM_TEXT[team]
#        textTeam = FONT_TEAM.render(str(teamName), 1, black)
#        screen.blit(textTeam, (5, 5))
            
    def recalculateLegalMoves(self):
        for unit in self.units:
            unit.setLegalMoves(self.getLegalMoves(unit))  
    
    def setOverlay(self, overlayImage, spaces):
        """Overlay spaces (an OverlayGroup) with the given overlay image"""
        self.overlayList = spaces
        self.overlayImage = overlayImage
        
    def showMovementRange(self, unit):
        """Sets an overlay to grey out all illegal moves"""
        illegalSpaces = OverlayGroup()
        for tile in self.terrain:
            if tile not in unit.legalMoves:
                illegalSpaces.add(Overlay(tile.pos, ILLEGAL_MOVEMENT_OVERLAY))
                #illegalSpaces.add(tile)
#        x = 0
#        y = 0
#        for row in self.terrain:
#            for space in row:
#                thisSpace = self.tileAt((x, y))
#                if thisSpace.rect not in unit.legalMoves:
#                    illegalSpaces.add(thisSpace)
#                x += 1
#            x = 0
#            y += 1
#        for thing in illegalSpaces:
#            print thing.pos
        self.setOverlay(ILLEGAL_MOVEMENT_OVERLAY, illegalSpaces)
        
    def hideMovementRange(self):
        self.overlay = None
        self.overlayList = OverlayGroup()
    
    def update(self):
        if self.turnStartTime:
            if (time.time() - self.turnStartTime) > 1.5:
                self.removeAnnouncements()
                self.turnStartTime = None
        self.draw()
        
    def draw(self):
        """Draw all terrain and units, and the overlay if it exists"""
        self.terrain.draw(screen)
        self.units.draw(screen)
        if self.overlayList:
            self.overlayList.draw(screen)
        if bool(self.announcers):
            self.announcers.runText()
            
    def addUnit(self, unitType, pos, team):
        """Adds a unit to the map, also returns that unit"""
        newUnit = unitType(pos, team)
        self.units.add(newUnit)
        newUnit.setLegalMoves(self.getLegalMoves(newUnit))
        newUnit.setNeighbors(self.getNeighbors(newUnit))
        self.recalculateLegalMoves() #other units' legal moves are affected by the new unit
        return newUnit
    
    def capture(self, unit, pos):
        pos.captureScore -= int(unit.hp)
        print "Capturing..."
        print pos.captureScore
        if pos.captureScore <= 0:
            print "Base captured"
            pos.changeTeam(unit.team)
        
    def getNeighbors(self, unit, getEnemyUnits=True, getAlliedUnits=True):
        """Returns a list of unit's neighbors in the following order:
        [up, down, left, right]
        
        The list will always be of length four. If there is no neighbor in a
        given direction, that element of the list will be False"""
        ##TODO: clean up this code
        neighbors = []
        try:
            neighbors.append(self.getUnitAt( \
                self.getTileAt((unit.pos.x, unit.pos.y - 1))))
        except NoUnitAtPositionError:
            pass
        try:
            neighbors.append(self.getUnitAt( \
                self.getTileAt((unit.pos.x, unit.pos.y + 1))))
        except NoUnitAtPositionError:
            pass
        try:
            neighbors.append(self.getUnitAt( \
                self.getTileAt((unit.pos.x - 1, unit.pos.y))))
        except NoUnitAtPositionError:
            pass
        try:
            neighbors.append(self.getUnitAt( \
                self.getTileAt((unit.pos.x + 1, unit.pos.y))))
        except NoUnitAtPositionError:
            pass
        
        #Remove units you aren't looking for from the list
        for neighbor in neighbors:
            if neighbor.isFriendlyTo(unit) and getAlliedUnits is False:
                neighbors.remove(neighbor)
            if not neighbor.isFriendlyTo(unit) and getEnemyUnits is False:
                neighbors.remove(neighbor)
                
        return neighbors
            
            
    def getUnitAt(self, mapPos):
        """Returns the unit on the given tile. 
        Raises a NoUnitAtPositionError if there is no unit there."""
        ## TODO: optimize, shouldn't have to loop
        for unit in self.units:
            if unit.pos == mapPos and not unit.selected:
                return unit
        raise NoUnitAtPositionError, mapPos
            
    def hasUnitAtPos(self, mapPos):
        """Returns True if there is a unit on the given tile.
        Otherwise False"""
        ## TODO: optimize, shouldn't have to loop
        for unit in self.units:
            if unit.pos == mapPos:
                return unit
        return False
    
    def hasUnselectedUnitAt(self, mapPos):
        ## TODO: optimize, shouldn't have to loop
        for unit in self.units:
            if unit.pos == mapPos and not unit.selected:
                return True
        return False
    
    def getLegalMoves(self, unit):
        """Returns a list of all spaces the given unit is allowed to move to."""
        movesWithinRange = self.getSpacesWithinMovementRange(unit)
        legalTiles = []
        for space in movesWithinRange:
            # If this space type obstructs the given unit, it's illegal
            if type(unit) in type(space).obstructs:
                pass
            # If there's a unit at this space
            elif self.hasUnitAtPos(space):
                ## If the unit at this space is friendly to the given unit, 
                ## the space is legal (but you won't be able to deselect there)
                if self.getUnitAt(space).isFriendlyTo(unit): 
                    #temp = self.getUnitAt(space)
                    legalTiles.append(space)
            else:
                legalTiles.append(space)
        return legalTiles
    
    def getSpacesWithinMovementRange(self, unit):
        """returns the list of positions within the given unit's movement range"""
        moveList = [unit.pos]
        #For each number of spaces this unit is allowed to move:
        for numOfSpacesInMove in xrange(1, unit.movementRange + 1):
            #Start with x at the maximum, and y at the minimum
            x = numOfSpacesInMove
            y = 0
            #While x hasn't reached 0, and y hasn't reached the maximum
            # (they should reach these points at the same time)
            while (x >= 0 and y <= numOfSpacesInMove):
                #Calculate moves in every direction with
                #  the current x and y values
                leftMove  = unit.pos.x - x
                rightMove = unit.pos.x + x
                upMove    = unit.pos.y - y
                downMove  = unit.pos.y + y
                #Add the move to the moveList as long as it doesn't
                #  put you off the edge of the screen
                if not (leftMove < 0 or upMove < 0):
                    moveList.append(self.getTileAt((leftMove, upMove)))
                if not (leftMove < 0 or downMove >= self.height):
                    moveList.append(self.getTileAt((leftMove, downMove)))
                if not (rightMove >= self.width or upMove < 0):
                    moveList.append(self.getTileAt((rightMove, upMove)))
                if not (rightMove >= self.width or downMove >= self.height):
                    moveList.append(self.getTileAt((rightMove, downMove)))
                x -= 1
                y += 1
        #remove duplicates from moveList
        d = {}
        for x in moveList: d[x]=x
        moveList = d.values()
        #print "Move List" + str(moveList)
        return moveList
    
    def removeDead(self):
        #Clean up the dead units
        for unit in self.units:
            if unit.hp <= 0:
                self.units.remove(unit)
                unit.pos.resetCaptureScore()
    


class OverlayGroup(pygame.sprite.RenderUpdates):
    """A group of Overlay objects, usually all the same"""
    def __init__(self):
        super(OverlayGroup, self).__init__()
        
class Overlay(pygame.sprite.Sprite):
    """A class for things that should be drawn on top of the map and units"""
    def __init__(self, (x, y), image):
        super(Overlay, self).__init__()
        self.pos = (x, y)
        self.rect = (x * TILE_W, y * TILE_H)
        self.image = image   


class TerrainGroup(pygame.sprite.RenderUpdates):
    """A group of TerrainTile objects, to be drawn to the screen"""
    def __init__(self):
        super(TerrainGroup, self).__init__()
                
class TerrainTile(pygame.sprite.Sprite):
    """Base class for all terrain"""
    obstructs = []
    def __init__(self, (x, y)):
        super(TerrainTile, self).__init__()
        self.image = None
        self.x = x
        self.y = y
        self.pos = (x, y)
        self.rect = (x * TILE_W, y * TILE_H)
        self.movementCost = {MOVE_MODE_FOOT : 0,
                             MOVE_MODE_TREAD: 0}
        self.team = False
        self.isCapturable = False
        self.captureScore = 0
        self.info = ""
        
    def draw(self):
        screen.blit(self.image, self.rect)
        
    def setImage(self, image):
        self.image = image
        
    def resetCaptureScore(self):
        if self.isCapturable:
            self.captureScore = 20
        
    
class PlainsTile(TerrainTile):
    """A tile of plains"""
    
    info = """Cover: 1"""
    terrainName = "Plains"
    def __init__(self, pos):
        super(PlainsTile, self).__init__(pos)
        self.image = plainsImage.convert()
        self.movementCost = {MOVE_MODE_FOOT : 1,
                             MOVE_MODE_TREAD: 1}
        
class ForestTile(TerrainTile):
    """A tile of forest"""
    
    info = "Cover: 2"
    terrainName = "Forest"
    def __init__(self, pos):
        super(ForestTile, self).__init__(pos)
        self.image = forestImage.convert()
        self.movementCost = {MOVE_MODE_FOOT : 1,
                             MOVE_MODE_TREAD: 2}
        
class SeaTile(TerrainTile):
    """A tile of Sea"""
    
    info = "Cover: 0"
    terrainName = "Sea"
    obstructs = [Unit.Infantry]
    
    def __init__(self, pos):
        super(SeaTile, self).__init__(pos)
        self.image = seaImage
        self.movementCost = {MOVE_MODE_FOOT : 3,
                             MOVE_MODE_TREAD: None}
        
class MountainTile(TerrainTile):
    """A tile of Mountains"""
    
    info = "Cover: 4"
    terrainName = "Mountain"
    obstructs = []
    def __init__(self, pos):
        super(MountainTile, self).__init__(pos)
        self.image = mountainImage
        self.movementCost = {MOVE_MODE_FOOT: 2,
                             MOVE_MODE_TREAD: None}
        

class RoadTile(TerrainTile):
    """A tile of road"""
    info = "Cover: 0"
    terrainName = "Road"
    obstructs = []
    def __init__(self, pos):
        super(RoadTile, self).__init__(pos)
        self.image = roadImage
        self.movementCost = {MOVE_MODE_FOOT : 1,
                             MOVE_MODE_TREAD: 1}


class BaseTile(TerrainTile):
    info = "Cover: 3"
    terrainName = "Base"
    def __init__(self, pos):
        super(BaseTile, self).__init__(pos)
        self.image = None
        self.movementCost = {MOVE_MODE_FOOT : 1,
                             MOVE_MODE_TREAD: 2}
        self.team = True
        self.isCapturable = True
        self.captureScore = 20
        
    def changeTeam(self, team):
        self.team  = team
        self.image = team.baseImage
        
#class CityTile(TerrainTile):
#    def __init__(self, pos):
#        super(CityTile, self).__init__(pos)
        
#Terrain lookup dictionary for maps        
TERRAIN_LOOKUP = { 1: PlainsTile,
                   2: ForestTile,
                   3: SeaTile,
                   4: BaseTile,
                   5: MountainTile,
                   6: RoadTile }
 

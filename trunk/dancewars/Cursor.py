import sys, os, pygame
from pygame.locals import *

from Constants import *
import Map
import Menu
import Unit

class UnitMove(object):
    def __init__(self, unit, startPos):
        self.unit = unit
        self.startPos = startPos
        self.pos = startPos

class CursorGroup(pygame.sprite.RenderUpdates):
    def __init__(self):
        super(CursorGroup, self).__init__()

class Cursor(pygame.sprite.Sprite):
    """The cursor"""
    def __init__(self, (x, y), map):
        super(Cursor, self).__init__()
        self.group = CursorGroup()
        self.group.add(self)
        self.image = cursorImage
        self.map = map
        #self.pos = (x, y)
        self.pos = map.getTileAt((x, y))
        self.rect = (x * TILE_W, y * TILE_H)
        self.selectedUnit = None
        self.moveStartPos = None
        self.movePointsUsed = 0
        self.menu = None
        #self.currentMove = None
        #self.menuGroup = Menu.MenuGroup()
        self.menuMode = False
    
    def changeImage(self, newImage):
        self.image = newImage
    
    def draw(self):
        self.group.draw(screen)
        #screen.blit(self.image, (self.rect[0], self.rect[1]))
        
    def drawMenu(self):
        self.menu.draw()
        #self.menuGroup.draw(screen)
        
    def startAttackMode(self):
        self.map.setAttackMode()  
        self.moveToNeighbor(-1)
    
    def cancelAttackMode(self):
        self._updatePos(self.selectedUnit.pos)
        self.map.endAttackMode()
        
    def beginMove(self, unit):
        self.selectedUnit = unit
        self.selectedUnit.selected = True
        self.moveStartPos = self.selectedUnit.pos
        self.movePointsUsed = 0
        self.map.showMovementRange(self.selectedUnit)
        
    def cancelMove(self):
        """Bring the unit back to its starting position, unmoved"""
        self._moveHelper(self.moveStartPos.pos, cancellingMove=True)
#        self.currentMove = None
        self.selectedUnit.selected = False
        self.selectedUnit = None
        self.moveStartPos = None
        self.map.hideMovementRange()
    
    def startBattle(self):
        """Starts a battle with self.currentMove.unit attacking and
        the unit at self.pos defending"""
        defender = self.map.getUnitAt(self.pos)
        attacker = self.selectedUnit
        defender.takeDamage(int(attacker.firepower * attacker.hp))
        attacker.takeDamage(int(defender.firepower * defender.hp))
        self.endBattle()
        
    def endBattle(self):
        """Cleans up after a battle"""
        self.map.removeDead()
        self.cancelAttackMode()
        self.deselectUnit()
    
    def selector(self):
        """Selects and deselects things"""
        if self.selectedUnit:
            if not self.map.hasUnselectedUnitAt(self.pos):
                self.menu = Menu.Menu([], MENU_POSITION)
                #self.menuGroup.add(self.menu)
                self.selectedUnit.setNeighbors(self.map.getNeighbors(self.selectedUnit))
                if self.selectedUnit.hasUnfriendlyNeighbors():
                    self.menu.add(Menu.MenuComponent("  Attack", self.startAttackMode))
                if self.selectedUnit.canCapture(self.pos):
                    self.menu.add(Menu.MenuComponent("  Capture", lambda: self.capture(self.selectedUnit, self.pos)))
                self.menu.add(Menu.MenuComponent("  Wait", self.deselectUnit))
                self.menu.add(Menu.MenuComponent("  Cancel", self.cancelMove))
                self.menuMode = True
        else:
            self.selectSpace()
            
    def capture(self, unit, pos):
        self.map.capture(unit, pos)        
        self.deselectUnit()
    
    def selectSpace(self):
        try:
            self.selectUnit()
        except Map.NoUnitAtPositionError:
            try:
                self.selectBase()
            except Map.NoBaseAtPositionError:
                pass
            
    def selectBase(self):
        thisTile = self.map.getTileAt(self.pos.pos)
        if type(thisTile) == Map.BaseTile:
            if thisTile.team == self.map.currentTeam:
                self.displayBaseMenu()
        else:
            raise Map.NoBaseAtPositionError, self.pos
    
    def selectUnit(self):
        thisUnit = self.map.getUnitAt(self.pos)
        if not thisUnit.movedThisTurn and self.map.currentTeam == thisUnit.team:
            #self.currentMove = UnitMove(thisUnit, self.pos)
            self.beginMove(thisUnit)
            
    def displayBaseMenu(self):
        self.menu = Menu.Menu([], MENU_POSITION)
        self.menu.add(Menu.MenuComponent("    Infantry", self.buildInfantry))
        self.menuMode = True
        
    def deselectUnit(self):
        self.selectedUnit.finishMove()
        self.selectedUnit.selected = False
        self.selectedUnit = None
        if self.moveStartPos != self.pos:
            self.moveStartPos.resetCaptureScore()
        self.moveStartPos = None
        self.map.hideMovementRange()
        self.map.recalculateLegalMoves()
        
    def onUnit(self):
        return self.map.hasUnitAtPos(self.pos)
        
    def move(self, dir):
        if dir == MOVE_UP:
            if self.pos.y != 0:
                newpos = (self.pos.x, self.pos.y - 1)
                self._moveHelper(newpos)
        elif dir == MOVE_DOWN:
            if self.pos.y != self.map.height - 1:
                newpos = (self.pos.x, self.pos.y + 1)
                self._moveHelper(newpos)
        elif dir == MOVE_LEFT:
            if self.pos.x != 0:
                newpos = (self.pos.x - 1, self.pos.y)
                self._moveHelper(newpos)
        elif dir == MOVE_RIGHT:
            if self.pos.x != self.map.width - 1:
                newpos = (self.pos.x + 1, self.pos.y)
                self._moveHelper(newpos)
        else:
            print "Error: direction not recognized."
            sys.exit()
            
    def moveToNeighbor(self, dir, alliedUnitsAllowed=False, enemyUnitsAllowed=True):
        """Moves the cursor to the position of the neighbor in the given dir.
        Assumes neighbor list to be ordered as follows:
        [up, down, left, right]"""
        
        #TODO: Fix this so you don't depend on Falses for empty spaces
        
        unit = self.selectedUnit
        if dir == -1:
            self._moveHelper(unit.neighbors[0].pos.pos)
        if dir == MOVE_UP:
            print "got up move"
            for neighbor in unit.neighbors:
                if neighbor.isNorthOf(unit):
                    print "got north neighbor"
                    self._moveHelper(neighbor.pos.pos)
                    break
        elif dir == MOVE_DOWN:
            for neighbor in unit.neighbors:
                if neighbor.isSouthOf(unit):
                    self._moveHelper(neighbor.pos.pos)
                    break
        elif dir == MOVE_LEFT:
            for neighbor in unit.neighbors:
                if neighbor.isWestOf(unit):
                    self._moveHelper(neighbor.pos.pos)
                    break
        elif dir == MOVE_RIGHT:
            for neighbor in unit.neighbors:
                if neighbor.isEastOf(unit):
                    self._moveHelper(neighbor.pos.pos)
                    break

#        if dir == -1:
#            for item in unit.neighbors:
#                if item is not False:
#                    dir = unit.neighbors.index(item)
#        if dir == MOVE_UP and unit.neighbors[0]:
#            newpos = (unit.pos.x, unit.pos.y - 1)
#            self._moveHelper(newpos)
#        elif dir == MOVE_DOWN and unit.neighbors[1]:
#            newpos = (unit.pos.x, unit.pos.y + 1)
#            self._moveHelper(newpos)
#        elif dir == MOVE_LEFT and unit.neighbors[2]:
#            newpos = (unit.pos.x - 1, unit.pos.y)
#            self._moveHelper(newpos)
#        elif dir == MOVE_RIGHT and unit.neighbors[3]:
#            newpos = (unit.pos.x + 1, unit.pos.y)
#            self._moveHelper(newpos)
#        else:
#            pass
            
    def _moveHelper(self, newpos, cancellingMove=False):
        newTile = self.map.getTileAt(newpos)
        if self.selectedUnit and not self.map.attackMode:
            #You're moving a unit
            self.movePointsUsed += newTile.movementCost[self.selectedUnit.movementMode]
            if self.movePointsUsed <= self.selectedUnit.movementRange or cancellingMove:
                self.selectedUnit.move(newTile)
                self._updatePos(self.selectedUnit.pos)                
        else:
            self._updatePos(newTile)
            
    def _updatePos(self, newTile):
        """Updates self.pos and self.rect with new coordinates
           Should only be called by moveHelper"""
        self.pos  = newTile
        self.rect = (newTile.x * TILE_W, newTile.y * TILE_H)
        
    ## UNIT BUILDING FUNCTIONS                  ##
    ## Responsible for placing units on the map ##
    def buildInfantry(self):
        newUnit = self.map.addUnit(Unit.Infantry, self.pos, self.pos.team)
        newUnit.finishMove()

import sys, os, pygame
from pygame.locals import *

from Constants import *

class IllegalMoveException(Exception):
    """Raised when a unit attempts to make an illegal move"""
    def __init__(self):
        self.value = value
    def __str__(self):
        return "Illegal Move"

class UnitGroup(pygame.sprite.RenderUpdates):
    """A group of units, to be drawn to the screen"""
    def __init__(self):
        super(UnitGroup, self).__init__()

class Unit(pygame.sprite.Sprite):
    """Base class for all units"""
    
    def __init__(self, pos):
        super(Unit, self).__init__()
        self.imageUnmoved = None
        self.imageMoved   = None
        self.pos = pos #pos is the tile on the map
        self.rect = (pos.x * TILE_W, pos.y * TILE_H) #rect is the position to draw to on the screen
        self.selected = False
        self.movementRange = None
        self.movedThisTurn = False
        self.legalMoves = None     #will be set by the map
        self.neighbors = []
        self.hp = 10.0
        self.capturer = False
        
    def _updatePos(self, newTile):
        """Update the unit's position. Should only be called by move"""
        self.pos = newTile
        self.rect = (self.pos.x * TILE_W, self.pos.y * TILE_H)
        
    def isNorthOf(self, unit):
        return self.pos.x == unit.pos.x and self.pos.y > unit.pos.y
    
    def isSouthOf(self, unit):
        return self.pos.x == unit.pos.x and self.pos.y < unit.pos.y
    
    def isWestOf(self, unit):
        return self.pos.x < unit.pos.x and self.pos.y == unit.pos.y
    
    def isEastOf(self, unit):
        return self.pos.x > unit.pos.x and self.pos.y == unit.pos.y
       
#    def draw(self, (x, y)):
#        
#        hpFont = pygame.font.SysFont("arial", 8)#pygame.font.Font(pygame.font.get_default_font(), 6)
#        hpFontColor = 0, 200, 200
#        text = hpFont.render(str(self.hp), 1, hpFontColor)
#        self.image.blit(text, (0, 0))
#        screen.blit(self.image, (x * TILE_W, y * TILE_H))
    
    def setNeighbors(self, neighbors):
        self.neighbors = neighbors
        
    def hasUnfriendlyNeighbors(self):
        for item in self.neighbors:
            if item is not False and not item.isFriendlyTo(self):
                return True
        return False
    
    def move(self, dest):
        if dest in self.legalMoves:
            self._updatePos(dest)
            
    def updateHP(self, newHP):
        self.hp = newHP
        displayHP = str(int(self.hp))
        textUnmoved = FONT_HP.render(displayHP, 1, black)
        textMoved = FONT_HP.render(displayHP, 1, white)
        self.imageMoved = self.imageMoved_orig.copy()
        self.imageUnmoved = self.imageUnmoved_orig.copy()
        self.imageMoved.blit(textMoved, (1, 1))
        self.imageUnmoved.blit(textUnmoved, (1, 1))
        self.image = self.imageUnmoved

    def finishMove(self):
        self.image = self.imageMoved
        self.movedThisTurn = True
    
    def setLegalMoves(self, legalMoves):
        self.legalMoves = legalMoves
        
    def newTurn(self):
        self.image = self.imageUnmoved
        self.movedThisTurn = False
        
    def isFriendlyTo(self, unit):
        return self.team == unit.team
    
    def takeDamage(self, amt):
        self.updateHP(self.hp - amt)
        
    def canCapture(self, pos):
        """Decides if this unit can capture the given position
        1. This unit must be able to capture things
        2. This position must be capturable
        3. This position must not already belong to this unit's team"""
        return self.capturer and \
               pos.isCapturable and \
               pos.team is not self.team



class Infantry(Unit):
    """An infantry unit"""
    name = "Infantry"
    def __init__(self, pos, team):
        super(Infantry, self).__init__(pos)
        if team.color == tan:
            self.imageUnmoved = infantryImage_tan.convert()
            self.imageMoved   = infantryMovedImage.convert()
        elif team.color == red:
            self.imageUnmoved = infantryImage_red.convert()
            self.imageMoved   = infantryMovedImage.convert()
        self.imageUnmoved_orig = self.imageUnmoved.copy()
        self.imageMoved_orig   = self.imageMoved.copy()
        self.image             = self.imageUnmoved
        self.movementRange     = MOVEMENT_RANGE_INFANTRY
        self.movementMode      = MOVE_MODE_FOOT
        self.legalMoves        = None
        self.team              = team
        self.updateHP(10.0)
        self.firepower         = .4
        self.capturer          = True

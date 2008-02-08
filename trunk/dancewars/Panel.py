import pygame

from Constants import *

class PanelGroup(pygame.sprite.RenderUpdates):
    def __init__(self):
        super(PanelGroup, self).__init__(self)

class Panel(object):
    """The information panel that appears at the bottom of the window"""
    def __init__(self, (x, y)):
        self.widgets = PanelGroup()
        self.size = (screen.get_width(), TILE_H * 2)
        self.surface = pygame.Surface(self.size)
        self.x = x
        self.y = y
        
    def addWidget(self, newWidget):
        self.widgets.add(newWidget)
        
    def update(self):
        self.widgets.update()
        self.draw()
    
    def draw(self):
        self.widgets.draw(self.surface)
        screen.blit(self.surface, (self.x, self.y))


     
class PanelWidget(pygame.sprite.Sprite):
    """A generic class for all widgets that appear in the information Panel"""
    def __init__(self, (x, y), width, height, cursor):
        super(PanelWidget, self).__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(black)
        self.rect = (x, y)
        self.width = width
        self.height = height
        self.cursor = cursor
        
class TerrainWidget(PanelWidget):
    """Provides info about the current terrain tile"""
    def __init__(self, pos, width, height, cursor):
        super(TerrainWidget, self).__init__(pos, width, height, cursor)
        self.updateInfo()
        
    def updateInfo(self):
        """Updates the internal state of the Widget"""
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(black)
        self.tile = type(self.cursor.pos)
        self.terrainImage = self.cursor.pos.image
        self.name = FONT_TERRAIN_INFO.render(self.tile.terrainName, 1, white)
        self.infoText = FONT_TERRAIN_INFO.render(self.tile.info, 1, white)
        
    def update(self):
        """Updates the widget's image to reflect the new internal state,
        then blits it to the screen"""
        self.updateInfo()
        self.image.blit(self.terrainImage, (1, 1))
        self.image.blit(self.name, (35, 0))
        self.image.blit(self.infoText, (35, 14))
        screen.blit(self.image, self.rect)
        

class UnitWidget(PanelWidget):
    """Provides info about the current unit, if any"""
    blackSurface = pygame.Surface((200, 40))
    blackSurface.fill(black)
    def __init__(self, pos, width, height, cursor):
        super(UnitWidget, self).__init__(pos, width, height, cursor)
        self.updateInfo()
        
    def updateInfo(self):
        """Updates the internal state of the Widget"""
        self.unit = self.cursor.onUnit()
        if self.unit:
            self.unitType = type(self.unit)
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill(black)
            self.unitImage = self.unit.image
            self.name = FONT_TERRAIN_INFO.render(self.unitType.name, 1, white)
            self.infoText = FONT_TERRAIN_INFO.render(self.unit.team.name, 1, white)
        else:
            self.image = UnitWidget.blackSurface
            
    def update(self):
        """Updates the widget's image to reflect the new internal state,
        then blits it to the screen"""
        self.updateInfo()
        if self.unit:
            self.image.blit(self.unitImage, (1, 1))
            self.image.blit(self.name, (35, 0))
            self.image.blit(self.infoText, (35, 14))
        screen.blit(self.image, self.rect)
        
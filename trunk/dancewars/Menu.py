import pygame

from Constants import *

class MenuGroup(pygame.sprite.RenderUpdates):
    def __init__(self):
        super(MenuGroup, self).__init__()
                

class Menu(pygame.sprite.Sprite):
    def __init__(self, components, pos):
        super(Menu, self).__init__()
        self.group = MenuGroup()
        self.group.add(self)
        self.rect = pos
        self.width = MENU_WIDTH
        self.height = MENU_MARGIN * 2
        self.components = MenuComponentGroup()
        self.componentsList = self.components.sprites()
        self.selectedOption = 0
        self.image = None
        self.image_orig = None
        self.menuCursorGroup = MenuCursorGroup()
        self.menuCursor = MenuCursor(self)
        self.menuCursorGroup.add(self.menuCursor)
    
    def add(self, component):
        self.components.add(component)
        component.setRect((MENU_MARGIN, self.height))
        self.componentsList = self.components.sprites()
        self.height += MENU_COMPONENT_HEIGHT
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(black)
        self.image_orig = self.image.copy()
        
    def draw(self):
        self.image = self.image_orig.copy()
        self.components.draw(self.image)
        self.menuCursorGroup.draw(self.image)
        #self.menuCursor.draw(self.image)
        self.group.draw(screen)
        #screen.blit(self.image, self.rect)
        
    def nextOption(self):
        self.selectedOption += 1
        if self.selectedOption >= len(self.componentsList):
            self.selectedOption = 0
        self.menuCursor.setPos((MENU_MARGIN, self.selectedOption))
    
    def prevOption(self):
        self.selectedOption -= 1
        if self.selectedOption < 0:
            self.selectedOption = len(self.componentsList) - 1
        self.menuCursor.setPos((MENU_MARGIN, self.selectedOption))
    
    def launchCallback(self):
        self.componentsList[self.selectedOption].callback()

class MenuCursorGroup(pygame.sprite.RenderUpdates):
    def __init__(self):
        super(MenuCursorGroup, self).__init__()
        
class MenuCursor(pygame.sprite.Sprite):
    """The cursor that highlights menu options"""
    def __init__(self, menu):
        super(MenuCursor, self).__init__()
        self.menu = menu 
        self.image = menuSelectImage
        self.rect = (2, 2)
    
    def setPos(self, (x, y)):
        self.rect = (MENU_MARGIN, y * MENU_COMPONENT_HEIGHT + MENU_MARGIN)
    
    def draw(self, dest):
        dest.blit(self.image, self.rect)



class MenuComponentGroup(pygame.sprite.RenderUpdates):
    def __init__(self):
        super(MenuComponentGroup, self).__init__()
        
    def draw(self, surface):
        super(MenuComponentGroup, self).draw(surface)

class MenuComponent(pygame.sprite.Sprite):
    """An option in the menu"""
    def __init__(self, name, callback):
        super(MenuComponent, self).__init__()
        self.name = name
        self.callback = callback
        self.rect = (MENU_MARGIN, MENU_MARGIN)
        self.image = FONT_MENU.render(str(self.name), 1, white)
        
    def setRect(self, pos):
        self.rect = pos
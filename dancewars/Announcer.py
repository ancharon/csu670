import time
import pygame

from Constants import *

class AnnouncerGroup(pygame.sprite.GroupSingle):
    """Group of Announcers to be drawn to the screen"""
    def __init__(self, thisMap, duration):
        super(AnnouncerGroup, self).__init__()
        self.duration = duration
        self.map = thisMap
        self.startTime = None
        
    def runText(self):
        if self.startTime:
            now = time.time()
            if now - self.startTime > self.duration:
                self.startTime = None
            elif not self.map.width * TILE_W < self.sprite.rect.right + 20:
                self.sprite.move(15, 0)
            elif (now - self.startTime) > 1:
                self.sprite.move(10, 0)
            self.sprite.draw()
        else: 
            self.startTime = time.time()
        

class Announcer(pygame.sprite.Sprite):
    def __init__(self, text, pos=(0, 10), font=FONT_TURN_ANNOUNCEMENT):
        super(Announcer, self).__init__()
        self.font = font
        self.text = self.font.render(text, 1, black)
        self.rect = self.text.get_rect(left=-self.text.get_width() - 10, top=pos[1])
        #self.rect = self.text.get_rect(left=pos[0], top=pos[1])
        self.image = self.text
    
    def setText(self, text):
        self.text = self.font.render(text, 1, black)
        self.image = self.text
        
    def move(self, x, y):
        self.rect = self.rect.move(x, y)
        
    def draw(self):
        screen.blit(self.text, self.rect)
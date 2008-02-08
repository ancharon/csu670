import pygame
from Constants import *

class Team(object):
    def __init__(self, name, color):
        self.color = color
        self.name = name
        self.money = 0
        self.bases = []
        self.cities = []
        self.baseImage = TEAM_BASE_IMAGES[color]
        
    def addCity(self, city):
        self.cities.append(city)
    
    def removeCity(self, city):
        self.cities.remove(city)
        
    def addBase(self, base):
        self.bases.append(base)
        
    def removeBase(self, base):
        self.bases.remove(base)
        
    def beginTurn(self):
        """Does all the things that should happen at the start of a turn.
        1. Gain $1000 per base/city.
        2. All units on allied cities/bases regain 2 HP."""
        self.money += len(self.bases) * 1000 + len(self.cities) * 1000

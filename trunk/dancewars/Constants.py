import os
import pygame


## Pygame setup
screen= pygame.display.set_mode((32 * 32, 22 * 32))
#screen = pygame.display.set_mode((1024, 768))

## Convenient Colors
black = 0, 0, 0
white = 255, 255, 255
tan = 235, 180, 158
green = 34, 139, 34
darkgreen = 47, 79, 47
blue = 0, 0, 155
red = 100, 0, 0

## Fonts
FONT_HP   = pygame.font.SysFont("arial", 10)
FONT_TEAM = pygame.font.SysFont("arial", 12)
FONT_MENU = pygame.font.SysFont("arial", 16)
FONT_TURN_ANNOUNCEMENT = pygame.font.SysFont("Impact", 18)
FONT_TERRAIN_INFO = pygame.font.SysFont("Impact", 12)

## Tile Width and Height
TILE_W = 32
TILE_H = 32
TILE = (TILE_W, TILE_H)

#Movement Directions
MOVE_UP    = 0
MOVE_DOWN  = 1
MOVE_LEFT  = 2
MOVE_RIGHT = 3

#Movement Modes
MOVE_MODE_FOOT = 0
MOVE_MODE_TREAD = 1

#Menu Constants
MENU_COMPONENT_HEIGHT = 32
MENU_MARGIN = 2
MENU_WIDTH = 103
MENU_POSITION = (48, 48)

#Teams have to be looked up by color to avoid circular imports
#TEAM_TEXT = {tan: "Tan Team",
#             red: "Red Team"}

ILLEGAL_MOVEMENT_OVERLAY = pygame.Surface.convert_alpha(pygame.image.load(os.path.join("img", "nomove_dark.png")))

####################
## Terrain Images ##
####################
tanBaseImage = pygame.Surface(TILE)
tanBaseImage.fill(pygame.colordict.THECOLORS["orange"])
redBaseImage = pygame.Surface(TILE)
redBaseImage.fill(pygame.colordict.THECOLORS["red"])
plainsImage = pygame.image.load(os.path.join("img", "plain-tile.png")).convert()
#plainsImage = pygame.Surface(TILE)
#plainsImage.fill(green)
forestImage = pygame.image.load(os.path.join("img", "tree-tile.png")).convert()
#forestImage = pygame.Surface(TILE)
#forestImage.fill(darkgreen)
seaImage = pygame.image.load(os.path.join("img", "sea-tile.png")).convert()
#seaImage = pygame.Surface(TILE)
#seaImage.fill(blue)
mountainImage = pygame.image.load(os.path.join("img", "mountain-tile.png")).convert()
roadImage = pygame.image.load(os.path.join("img", "road-tile.png")).convert()
TEAM_BASE_IMAGES = {tan: tanBaseImage,
                    red: redBaseImage}

#################
## Unit Images ##
#################
infantryImage_tan = pygame.Surface(TILE)
infantryImage_tan.fill(tan)
infantryImage_red = pygame.Surface(TILE)
infantryImage_red.fill(red)
infantryMovedImage = pygame.Surface(TILE)
infantryMovedImage.fill(black)

#################
## Misc Images ##
#################
cursorImage = pygame.Surface(TILE)
cursorImage = pygame.Surface.convert_alpha(pygame.image.load(os.path.join("img", "cursor.png")))
menuSelectImage = pygame.Surface.convert_alpha(pygame.image.load(os.path.join("img", "menu_select.png")))

##########################
## Unit Movement Ranges ##
##########################
MOVEMENT_RANGE_INFANTRY = 3
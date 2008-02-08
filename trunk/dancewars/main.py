import sys, os, pygame, time
from pygame.locals import *

pygame.init()
#pygame.font.init()
pygame.key.set_repeat(100, 50)

from Constants import *
import Unit, Map, Cursor, Team, Panel


p = 1 #plains
f = 2 #forest
s = 3 #sea
b = 4 #base
m = 5 #mountain
r = 6 #road

#map = Map(terrain=[[p, p, f, f, f, f, p],
#                   [p, p, p, p, f, f, f],
#                   [p, p, p, p, f, f, f],
#                   [p, p, p, p, p, f, p]])

turnStart = None
TEAM_TAN = Team.Team("Tan Team", tan)
TEAM_RED = Team.Team("Red Team", red)

map = Map.Map([[p, p, f, f, b, f, p, s, s, s, s, s],
               [p, p, p, p, f, f, f, s, s, s, s, s],
               [p, p, p, p, f, f, f, p, s, s, s, s],
               [p, p, p, p, p, f, p, p, s, s, s, s],
               [p, p, p, p, p, p, p, p, r, p, s, s],
               [p, p, b, p, p, p, p, p, r, p, p, s],
               [p, p, m, m, p, p, p, p, r, p, p, p],
               [p, p, m, m, p, p, p, p, r, p, p, p],
               [m, m, m, m, p, p, p, p, r, p, p, p],
               [p, p, p, p, p, p, p, p, r, p, p, p]],
               [TEAM_TAN, TEAM_RED], [TEAM_TAN, TEAM_RED])



map.addUnit(Unit.Infantry, map.getTileAt((5, 5)), TEAM_TAN)
map.addUnit(Unit.Infantry, map.getTileAt((4, 4)), TEAM_TAN)
map.addUnit(Unit.Infantry, map.getTileAt((5, 2)), TEAM_RED)

clock = pygame.time.Clock()

cursor = Cursor.Cursor((2, 2), map)
panel  = Panel.Panel((5, map.height * TILE_H + 5))
print map.height
panel.addWidget(Panel.TerrainWidget((0, 0), 200, 40, cursor))
panel.addWidget(Panel.UnitWidget((205, 0), 200, 40, cursor))
while 1:
    for event in pygame.event.get():
        #start = time.time()
        #Quit if the window is closed or the user hits escape
        if event.type == pygame.QUIT: sys.exit()
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit()
        if cursor.menuMode: #The end-of-move menu should be displayed
            if event.type == KEYDOWN:
                if event.key == K_DOWN: #Go to the next option down
                    cursor.menu.nextOption()
                if event.key == K_UP: #Go to the next option up
                    cursor.menu.prevOption()
                if event.key == K_SPACE: #Choose this option and close the menu
                    cursor.menuMode = False
                    cursor.menu.launchCallback()
        elif map.attackMode: #Player has chosen to attack
            if event.type == KEYDOWN:
                if event.key == K_LEFT: #Move cursor to left neighbor
                    cursor.moveToNeighbor(MOVE_LEFT)
                if event.key == K_RIGHT: #right neighbor
                    cursor.moveToNeighbor(MOVE_RIGHT)
                if event.key == K_UP: #up neighbor
                    cursor.moveToNeighbor(MOVE_UP)
                if event.key == K_DOWN: #down neighbor
                    cursor.moveToNeighbor(MOVE_DOWN)
                if event.key == K_SPACE: #attack the selected neighbor
                    cursor.startBattle()
                if event.key == K_c: #cancel attack
                    cursor.cancelAttackMode()
                if event.key == K_f: #cancel attack and end move
                    cursor.cancelAttackMode()
                    cursor.deselectUnit()
        else: #Moving the cursor (and possibly a unit with it)
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    cursor.move(MOVE_LEFT)
                if event.key == K_RIGHT:
                    cursor.move(MOVE_RIGHT)
                if event.key == K_UP:
                    cursor.move(MOVE_UP)
                if event.key == K_DOWN:
                    cursor.move(MOVE_DOWN)
                if event.key == K_SPACE:
                    #Select or deselect a unit (deselection starts menu mode first)
                    cursor.selector()
                if cursor.selectedUnit: #there's a unit selected
                    if event.key == K_c:
                        cursor.cancelMove()
                else: #No selected unit
                    #End this turn and change to the next
                    if event.key == K_e:
                        map.changeTurns()
                #Something happened, update the panel
                panel.update()
        
    map.update()
    cursor.draw()
    if cursor.menuMode:
        cursor.drawMenu()
    clock.tick(80)
    #print clock.get_fps()
    pygame.display.flip()
        

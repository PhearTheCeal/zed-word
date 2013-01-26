#!/usr/bin/python
import pygame
import sys
import os
from pygame.locals import *
import sqlite3 as sqlite

pygame.init() # this paragraph is just your standard pygame stuff
screen_width = 640 
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height), RESIZABLE, 32)
pygame.display.set_caption("Map Viewer")


def display(camera_x, camera_y):
    for tile in tilelist.keys():
        r = ((tile[0]*tile_size) + camera_x, (tile[1]*tile_size) + camera_y)
        if r[0] > 0 and r[1] > 0 and r[0] < screen_width and r[1] < screen_height:
            screen.blit(tileset[tilelist[tile]], r)
    for o in object_list:
        o.draw()
        

def right_widget(current_tile):
    width = 30
    widget_surface = pygame.Surface((30, screen_height))
    widget_surface.fill((40,200,90))
    y2 = 10
    x2 = 5
    for key in tileset:
        r = tileset[key].get_rect().move((x2, y2))
        widget_surface.blit(tileset[key], r)
        if Rect(x2+screen_width-30, y2, 20, 20).collidepoint(x,y):
            pygame.draw.rect(widget_surface, (0,0,0), (x2, y2, 20, 20), 2)
            if event.type == MOUSEBUTTONUP:
                current_tile = key
        y2 += 30
    screen.blit(widget_surface, (screen_width-30, 0))
    return current_tile


def tile_adder():
    in_screen = Rect(0,0,screen_width-30, screen_height).collidepoint(x,y)
    if in_screen:
        pygame.draw.rect(screen, (255,0,0), ((((x-int(camera_x))/tile_size)*tile_size) + int(camera_x), # magic, and...
        (((y-int(camera_y))/tile_size)*tile_size + int(camera_y)), 20, 20), 2) # more magic that draws the red outline
        
        if current_tile not in object_types:
            if pygame.mouse.get_pressed()[0] == 1 and in_screen:
                tilelist[((x+-int(camera_x))/tile_size, (y+-int(camera_y))/tile_size)] = current_tile
    
            elif pygame.mouse.get_pressed()[2] == 1 and in_screen:
                tile = ((x+-int(camera_x))/tile_size, (y+-int(camera_y))/tile_size)
                if tile in tilelist: # without this, keyerror occurs if tile nonexistiant
                    del tilelist[tile]
                    
        elif current_tile in object_types:
            if pygame.mouse.get_pressed()[0] == 1 and in_screen:
                object_list.append( object_base( (x+-int(camera_x))/tile_size, (y+-int(camera_y))/tile_size, current_tile ) )
            elif pygame.mouse.get_pressed()[2] == 1 and in_screen:
                for o in object_list:
                    if o.rect.collidepoint(x,y): object_list.remove(o)
class object_base:
    # It has basic stuff that is needed by needy objects
    def __init__(self, x, y, type):
        self.x, self.y = x, y
        self.type = type
        self.image = tileset[type]
        self.image.set_colorkey(self.image.get_at((0,0)))
    def draw(self):
        self.rect = self.image.get_rect().move((self.x*tile_size + camera_x, self.y*tile_size + camera_y))
        screen.blit(self.image, self.rect)

# All of our (bad practice) global variables
object_types = ["house", "tree"] # This will be expanded as we get more objects
object_list = [] # Stores all objects
tileset = dict([(f.split('.')[0], pygame.image.load('tiles/'+f)) for f in os.listdir('tiles') if 'png' in f])
tile_size = 20
current_tile = "dirt"
camera_x, camera_y = screen_width/2, screen_height/2 # can equal anything, merely for looks
camera_speed = ((screen_width+screen_height)/2) * 0.0036
camera_speed_real = camera_speed
flag = 0 # hacky way to make sure Ctr-S isn't held down

connection = sqlite.connect("database.db") # I'm guessing all this loads the map
cursor = connection.cursor()
objects = cursor.execute("SELECT position, name FROM tiles")
tilelist = {}
for line in objects:
    if line[1].encode("UTF-8") in object_types: #load objects
        x,y = eval(line[0])
        object_list.append( object_base(x, y, line[1].encode("UTF-8")) )
    else:
        position = eval(line[0])
        tilelist[position] = line[1].encode("UTF-8")
cursor.close()
connection.close()

while True:
    for event in pygame.event.get(): 
        if event.type == QUIT: 
            pygame.quit()
            sys.exit()
        if event.type == VIDEORESIZE: 
            screen_width, screen_height = event.size
            camera_speed_real = ((screen_width+screen_height)/2) * 0.0036 # Camera speed adjusts to the size
            pygame.display.set_mode(event.size, RESIZABLE, 32)
    pressed_keys = pygame.key.get_pressed() #this paragraph deals with scrolling up and down
    if pressed_keys[K_ESCAPE]:
        pygame.quit()
        sys.exit()
    screen.fill((0, 0, 0))
    x,y = pygame.mouse.get_pos()
    if pygame.key.get_mods()&1: camera_speed = camera_speed_real * 3
    else: camera_speed = camera_speed_real
    if pygame.mouse.get_focused() == True and (pygame.mouse.get_pressed()[0]&1 or pygame.mouse.get_pressed()[0] == 1):
        if Rect(0, 0, 20, screen_height).collidepoint(x, y): # screen left
            camera_x += camera_speed
        if Rect(screen_width-20-30, 0, 20, screen_height).collidepoint(x, y): # screen right
            camera_x -= camera_speed
        if Rect(0, 0, screen_width-30, 20).collidepoint(x, y): # screen top
            camera_y += camera_speed
        if Rect(0, screen_height-20, screen_width-30, 20).collidepoint(x, y): # screen bottom
            camera_y -= camera_speed
    if pressed_keys[K_DOWN] or (pressed_keys[K_s] and not pygame.key.get_mods()&64):
        camera_y -= camera_speed
    if pressed_keys[K_UP] or pressed_keys[K_w]:
        camera_y += camera_speed
    if pressed_keys[K_RIGHT] or pressed_keys[K_d]:
        camera_x -= camera_speed
    if pressed_keys[K_LEFT] or pressed_keys[K_a]:
        camera_x += camera_speed
    if pressed_keys[K_s] and pygame.key.get_mods()&64 and flag != 1:
        connection = sqlite.connect("database.db")
        cursor = connection.cursor()
        tilesInBase = cursor.execute("select id from tiles") # note to self: change tiles table to have x, y rows (int)
        for base in tilesInBase:
            cursor.execute("delete from tiles where id=" + str(base[0]))
        for tile in tilelist:
            cursor.execute("insert into tiles values (null,?,?)", (str(tile), tilelist[tile]))
        for o in object_list:
            cursor.execute("insert into tiles values (null,?,?)", (str((o.x, o.y)), o.type))
        cursor.close()
        connection.commit()
        connection.close()
        flag = 1
    if pygame.key.get_mods() == 0: flag = 0
    display(camera_x, camera_y)
    current_tile = right_widget(current_tile)
    tile_adder()
    pygame.display.update()
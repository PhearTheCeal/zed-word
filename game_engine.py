from game_classes import *
import pygame, math, random
from pygame.locals import *

class Game:
    """
    Game class handles everything in it's update(). It also holds all of the objects, the hero, and the world.
    
    I designed it to be the only class that can call other objects functions this way. Dunno if I like it or not
    but it works.
    """
    
    def __init__(self):
        self.objects = {
            "bullets":[],
            "ammo":[],
            "health packs":[],
            "walls":[],
            "barricades":[],
            "zombies":[]
        }
        
        self.world = World(pygame.display.set_mode((screen_width, screen_height)))
        self.world.generate()

        for i in range(-50, 50):
            for j in range(-50, 50):
                r = random.random()
                if r < 0.005:
                    self.objects['ammo'].append(Ammo(i,j))
                elif r > 0.995:
                    self.objects['health packs'].append(Health_Pack(i,j))
                elif r > 0.59 and r < 0.6:
                    self.objects['zombies'].append(Zombie(i,j))

        self.hero = Hero()
    def update(self):
        self.world.update(self.objects, self.hero)
        self._handle_move_input()
        self._handle_fire_input()
        self._handle_bullets()
        self._handle_zombies()
    
    def _handle_move_input(self):
        pressed_keys = pygame.key.get_pressed()
        camera_speed = self.hero.speed # So that it syncs up
        movx, movy = 0, 0
        if pressed_keys[K_DOWN] or pressed_keys[K_s]:
            self.world.camera_y -= camera_speed
            movy = 1
        elif pressed_keys[K_UP] or pressed_keys[K_w]:
            self.world.camera_y += camera_speed
            movy = -1
        if pressed_keys[K_RIGHT] or pressed_keys[K_d]:
            self.world.camera_x -= camera_speed
            movx = 1
        elif pressed_keys[K_LEFT] or pressed_keys[K_a]:
            self.world.camera_x += camera_speed
            movx = -1
       	# See if his new position is valid then move (or not move) him there
        if self._handle_collision(movx*self.hero.speed, movy*self.hero.speed) == False:
            self.hero.move(movx, movy)
        else:
            self.world.camera_x -= (self.hero.x + self.world.camera_x) - screen_width/2
            self.world.camera_y -= (self.hero.y + self.world.camera_y) - screen_height/2
            
    def _handle_collision(self, x, y):
        for obtype in self.objects:
            # collidelist goes through all the objects and checks if the hero collides with any of them. If not, returns False
            i = self.hero.get_rect().move(x,y).collidelist([o.get_rect() for o in self.objects[obtype]])
            if i != -1:
                o = self.objects[obtype][i]
                if obtype == "health packs":
                    self.hero.mod_hp(o.get_ammo())
                    self.objects[obtype].remove(o)
                if obtype == "ammo":
                    self.hero.mod_ammo(o.get_ammo())
                    self.objects[obtype].remove(o)
                if obtype == "zombies":
                    self.hero.mod_hp(-0.5)
                return True
        return False
    
    def _handle_fire_input(self):
        if pygame.mouse.get_pressed()[0] == 1 and self.hero.get_ammo() > 0:
            x, y = self.hero.x , self.hero.y
            angle = math.atan2(self.world.mousepos[1] - (y+self.world.camera_y), self.world.mousepos[0] - (x+self.world.camera_x))*180/math.pi*-1
            self.objects["bullets"].append(Bullet(x, y, angle))
            self.hero.mod_ammo(-1)

    def _handle_bullets(self):
        for b in self.objects["bullets"]:
            if b.chk_alive() == False:
                self.objects["bullets"].remove(b)
        
    
    def _handle_zombies(self):
        dead_zombies = []
        for zombie in self.objects["zombies"]:
            i = zombie.get_rect().collidelist([o.get_rect() for o in self.objects['bullets']])
            if i != -1:
                self.objects['bullets'].pop(i)
                zombie.mod_hp(-5)
            if zombie.is_dead():
                dead_zombies.append(zombie)

            hx = (screen_width/2)-8
            hy = (screen_height/2)-8
            distance_from_zombie_to_hero = math.sqrt( abs(zombie.get_rect().centerx - hx)**2 + abs(zombie.get_rect().centery - hy)**2 )
            
            if distance_from_zombie_to_hero < 100:
                zombie.aiState = "chase"
            else:
                zombie.aiState = "wander"
        for z in dead_zombies:
            self.objects["zombies"].remove(z)
            del z
            
        # self._make_zombies_chase_hero()
        # self._have_close_zombies_attack_hero()
        # self._get_next_move_in_A_star_algo()
        
import pygame, math, random

screen_width = 640
screen_height = 480

class World:
    """ This class will store all the world information, including
    the screen, camera xy, and mouseposition. On update() it is tasked
    with drawing all of it's tiles to the screen, then drawing all the 
    objects on the world.
    
    When it calls an objects update function, it passes the parameter self
    to the method. This way, the objects update routine can access all of
    the world objects info. It uses this info to know where to blit to.
    """

    def __init__(self, screen, world_data="test.world"):
        self.tiles = []
        self.screen = screen
        self.camera_x, self.camera_y = screen_width/2, screen_height/2
    def update(self, objects, hero):
        self.mousepos = pygame.mouse.get_pos()
        self.screen.fill((0, 0, 0))
        self._draw_tiles()
        self._display(objects, hero)
        pygame.display.update()
    
    def generate(self):
        for i in range(-50, 50):
            for j in range(-50, 50):
                self.tiles.append(Tile(i,j))

    def _draw_tiles(self):
        for tile in self.tiles:
            tile.update(self)
            
    def _display(self, objects, hero):
        for otype in objects:
            for o in objects[otype]:
                o.update(self)
        hero.update(self)
        if hero.dead == True:
            x = random.randint(-40*20, 40*20)
            y = random.randint(-40*20, 40*20)
            hero.x = x
            hero.y = y
            self.camera_x = x
            self.camera_y = y
            hero.mod_hp(1000)
        
        

class Hero:
    """
    Base class for the hero. Right now he has a bunch of silly get_*() methods
    for getting information about his object. I figured it would be easier to 
    just modify what the methods return than having some outside code manually
    get and modify things from the object. e.g. Hero.get_hp() instead of Hero.hp
    
    His rect is based off of his base_sprite, so that when he rotates his rect
    doesn't magically get bigger.
    
    Needs work...
    """
    
    def __init__(self, ammo=20, hp=50, max_hp=50):
        self.x, self.y = 0, 0
        self.ammo = ammo
        self.hp = hp
        self.max_hp = max_hp
        self.carrying_ob = False
        self.base_sprite = pygame.image.load("sprites/hero.png")
        self.cur_sprite = pygame.image.load("sprites/hero.png")
        self.speed = 5
        self.dead = False
    def move(self, x, y):
        self.x += x*self.speed
        self.y += y*self.speed
    def mod_ammo(self, ammount):
        self.ammo += ammount
    def mod_hp(self, ammount):
        if self.hp + ammount > self.max_hp:
            self.hp = self.max_hp
        else:
            self.hp += ammount

        if self.hp < 0:
            self.dead = True
        else:
            self.dead = False


    def is_dead(self):
        return self.dead
    def get_ammo(self):
        return self.ammo
    def get_hp(self):
        return self.hp
    def set_carrying_ob(self, bool):
        self.carrying_ob = bool
    def get_carrying_ob(self):
        return self.carrying_ob
    def get_rect(self):
        return pygame.Rect((screen_width/2), (screen_height/2), self.base_sprite.get_width(), self.base_sprite.get_height())
    def update(self, world):
        self._draw(world)
        self._draw_hp_bar(world)
        self._draw_ammo_remaining(world)
        
    def _draw(self,world):
        self.cur_sprite = pygame.transform.rotate(
            self.base_sprite, math.atan2(world.mousepos[1] - self.y-world.camera_y, world.mousepos[0] - self.x-world.camera_x)*180/math.pi*-1)
        self.cur_sprite.set_colorkey(self.cur_sprite.get_at((0,0)))
        world.screen.blit(self.cur_sprite, (self.x + world.camera_x, self.y + world.camera_y))
        
    def _draw_hp_bar(self, world):
        # Here are the base dimensions of the bar
        bar_width = 100
        bar_height = 10
        bar_y = screen_height - 15
        bar_x = 5
        
        # draws the outline of the health 
        pygame.draw.rect( world.screen, (0,255,0), (bar_x, bar_y, bar_width, bar_height), 2 )
        # Draw the actualy health bar, width depends on player health
        hp_bar_width = (float(self.hp)/self.max_hp) * bar_width
        pygame.draw.rect( world.screen, (0,255,0), (bar_x, bar_y, hp_bar_width, bar_height) )
        
    def _draw_ammo_remaining(self, world):
        # Create a font
        font = pygame.font.Font(None, 17)
        
        # Render the text
        text = font.render(str(self.ammo), True, (255,
        255, 0), (159, 182, 205))
        
        # Create a rectangle
        textRect = text.get_rect()
        
        # Position the rectangle
        textRect.bottom = screen_height - 15
        textRect.right = screen_width - 5
        
        # Blit the text
        world.screen.blit(text, textRect)

class Zombie:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 1
        self.speed = 0.1
        self.attacking = False
        self.base_sprite = pygame.image.load("sprites/zombie.png")
        self.sprite = self.base_sprite
        self.sprite_width = self.sprite.get_width()
        self.sprite_height = self.sprite.get_height()
        self.sprite.set_colorkey((255,255,255))
        self.aiState = None
        self.angle = 0
        self.dead = False
    def get_rect(self):
        return self.rect
    def update(self, world):

        self._ai()
        self._draw(world)
        real_x = self.x*self.sprite_width + world.camera_x
        real_y = self.y*self.sprite_height + world.camera_y
        self.rect = pygame.Rect(real_x, real_y, self.sprite_width, self.sprite_height)
    def _draw(self, world):
        self.sprite = pygame.transform.rotate(self.base_sprite, self.angle)
        pos = ((self.x*self.sprite_width) + world.camera_x, (self.y*self.sprite_width + world.camera_y))
        world.screen.blit(self.sprite, pos)
    def _ai(self):
        if self.aiState == "chase":
            zombie_rect = self.get_rect()
            zombie_x = zombie_rect.centerx
            zombie_y = zombie_rect.centery
            hx = (screen_width/2)+8 # Plus 8 to get center of hero
            hy = (screen_height/2)+8

            self.angle = math.atan2(hy - zombie_y, hx - zombie_x)*180/math.pi*-1
            distance_from_zombie_to_hero = math.sqrt( abs(zombie_x - hx)**2 + abs(zombie_y - hy)**2 )
            
            if distance_from_zombie_to_hero > 16: # Check for adequate distance between center of zombie and center of hero
                self._move_forward()
                
        elif self.aiState == "wander":
            self.angle = random.randint(int(self.angle-10), int(self.angle+10)) # This makes him "wander"
            self._move_forward()
            
    def _move_forward(self):
            # This is all the same as the bullet vector stuff
            self.x += self.speed*math.sin(math.radians(self.angle+90))
            self.y += self.speed*math.cos(math.radians(self.angle+90))

    def attack(self):
        if attacking:
            pass
        else:
            attacking = True
    def mod_hp(self, ammount):
        self.hp += ammount

        if self.hp < 0:
            self.dead = True

    def is_dead(self):
        return self.dead
        

class Tile:
    """
    Tile class is here. Don't know if we'll ever have to use the walkabilty status.
    If we don't, I'll just remove it later.
    """
    
    def __init__(self, x, y, walkable=True, sprite="tiles/default.png"):
        self.x, self.y = x, y
        self.sprite = pygame.image.load(sprite)
        self.walkable = walkable
    def get_pos(self):
        return (self.x, self.y)
    def set_sprite_surface(self, sprite):
        self.sprite = sprite
    def get_walkable(self):
        return self.walkable
    def update(self, world):
        self._draw(world)
    def _draw(self, world):
        pos = ((self.x*self.sprite.get_width()) + world.camera_x, (self.y*self.sprite.get_width() + world.camera_y))
        world.screen.blit(self.sprite, pos)

class Bullet:
    """
    Bullet gets it's x, y, and angle based off of the hero's x, y, and angle.
    
    On update(), besides blitting, it also moves.
    
    I manually set the colorkey, instead of picking the color at (0,0). This way
    if the bullet is rotated just right it won't pick up the bullets color accidently
    
    It stays in the game until it collides with a zombie or expires from existing too long
    """
    
    def __init__(self, x, y, angle):
        self.x, self.y = x, y
        self.angle = angle
        self.speed = 25
        self.sprite = pygame.transform.rotate(pygame.image.load("sprites/bullet.png"), self.angle)
        self.sprite.set_colorkey((255,255,255))
        self.life_timer = 30
        self.rect = pygame.Rect(0,0,0,0)
        self.dead = False
    def update(self, world):
        self._move()
        self._draw(world)
        self.life_timer -= 1
        real_x = self.x + world.camera_x
        real_y = self.y + world.camera_y
        self.rect = pygame.Rect(real_x, real_y, self.sprite.get_width(), self.sprite.get_height())
    def get_rect(self):
        return self.rect
    def chk_alive(self):
        if self.life_timer < 1:
            return False
        else:
            return True
    def _move(self):
        self.x += self.speed*math.sin(math.radians(self.angle+90))
        self.y += self.speed*math.cos(math.radians(self.angle+90))
    def _draw(self, world):
        pos = (self.x + world.camera_x, (self.y + world.camera_y))
        world.screen.blit(self.sprite, pos)

class Ammo:
    """
    This is the base class for all the pickups. Maybe I'll make a pickup class
    and have Ammo and Health_pack etc. inheret from that but who knows.
    
    It has a move function so that the hero can pick it up and move it around.
    """
    
    # Not yet sure how we are going to implement different ammo types yet.
    def __init__(self, x, y, ammount=10):
        self.x, self.y = x, y
        self.sprite = pygame.image.load("sprites/ammo.png")
        self.sprite.set_colorkey((255,255,255))
        self.ammount = ammount # or whatever
    def move(self, x, y):
        self.x += x
        self.y += y
    def get_ammo(self): # Calls to this method should be followed by deletion of said object
        return self.ammount
    def get_rect(self):
        return self.rect
    def update(self, world):
        self._draw(world)
        real_x = self.x*self.sprite.get_width() + world.camera_x
        real_y = self.y*self.sprite.get_height() + world.camera_y
        self.rect = pygame.Rect(real_x, real_y, self.sprite.get_width(), self.sprite.get_height())
    def _draw(self, world):
        pos = ((self.x*self.sprite.get_width()) + world.camera_x, (self.y*self.sprite.get_width() + world.camera_y))
        world.screen.blit(self.sprite, pos)

class Health_Pack(Ammo):
    """
    Pretty simple
    """
    
    def __init__(self, x, y, ammount=20):
        self.x, self.y = x, y
        self.sprite = pygame.image.load("sprites/health pack.png")
        self.ammount = ammount # or whatever
    def update(self, world):
        self._draw(world)
        real_x = self.x*self.sprite.get_width() + world.camera_x
        real_y = self.y*self.sprite.get_height() + world.camera_y
        self.rect = pygame.Rect(real_x, real_y, self.sprite.get_width(), self.sprite.get_height())
    def _draw(self, world):
        pos = ((self.x*self.sprite.get_width()) + world.camera_x, (self.y*self.sprite.get_width() + world.camera_y))
        world.screen.blit(self.sprite, pos)

class Wall:
    """
    Also a base class for Barricade, since there isn't much of a difference between the two.
    
    Since these have health and aren't walkable, I wasn't sure if we'd have to use tiles that
    have a walkabilty status. get_alive() will be checked in the main game loop, if it isn't alive
    the game will delete the object.
    """
    
    def __init__(self, x, y):
        self.x, self.y = x, y
        # Maybe we could have the sprite shrink as hp decreases
        self.sprite = pygame.image.load("sprites/wall.png")
        self.sprite.set_colorkey( self.sprite.get_at((0,0)) )
        self.hp = 50 # or whatever
        self.max_hp = 50 # or whatever
    def get_alive(self):
        return self.hp > 0
    def mod_hp(self, ammount):
        self.hp += ammount
    def get_rect(self):
        return self.rect
    def update(self, world):
        self._draw(world)
        real_x = self.x*self.sprite.get_width() + world.camera_x
        real_y = self.y*self.sprite.get_height() + world.camera_y
        self.rect = pygame.Rect(real_x, real_y, self.sprite.get_width(), self.sprite.get_height())
    def _draw(self, world):
        world.screen.blit(self.sprite, ((self.x*self.sprite.get_width() + world.camera_x, self.y*self.sprite.get_height() + world.camera_y)))

class Barricade(Wall):
    """
    The only difference between this and wall, as you can see, is health ammount,
    sprite, and the ability to move around.
    """
    def __init__(self, x, y):
        self.x, self.y = x, y
        # Maybe we could have the sprite shrink as hp decreases
        self.sprite = pygame.image.load("sprites/barricade.png")
        self.hp = 25 # or whatever
        self.max_hp = 25 # or whatever
    def move(self, x, y):
        self.x += x
        self.y += y
        
from game_engine import Game
import pygame, sys
from pygame.locals import *

pygame.init()
game = Game()
c = pygame.time.Clock()
while __name__ == "__main__":
    c.tick(30)
    game.update()
    for event in pygame.event.get(): 
        if event.type == QUIT: 
            pygame.quit()
            sys.exit()

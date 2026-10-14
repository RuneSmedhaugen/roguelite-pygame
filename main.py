import pygame
from core.game import Game

pygame.init()

BASE_WIDTH = 0
BASE_HEIGHT = 0
FULLSCREEN = True
screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()

game = Game()
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()

    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()[0]

    game.update(keys, mouse_pos, mouse_click)

    # 🎨 Game handles ALL rendering
    game.draw(screen, mouse_pos)

    pygame.display.flip()

pygame.quit()
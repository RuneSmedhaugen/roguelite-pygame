import pygame
from core.game import Game

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

game = Game()
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # 🧠 Game handles ALL logic
    game.update(keys)

    # 🎨 Game handles ALL rendering
    game.draw(screen)

    pygame.display.flip()

pygame.quit()
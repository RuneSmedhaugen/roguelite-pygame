import pygame
from core.game import Game
from core.music import MusicPlaylist

pygame.init()


DISPLAY_MODE = "fullscreen"
DISPLAY_SIZE = (0, 0)
DISPLAY_INDEX = 0

def change_display(mode, size, display_index=0):
    """Apply a display mode. Display creation stays owned by main.py."""
    global screen, DISPLAY_MODE, DISPLAY_SIZE, DISPLAY_INDEX

    if mode == "fullscreen":
        flags = pygame.FULLSCREEN
        requested_size = size
    elif mode == "borderless":
        desktop_sizes = pygame.display.get_desktop_sizes()
        if desktop_sizes:
            requested_size = desktop_sizes[display_index] if display_index < len(desktop_sizes) else desktop_sizes[0]
        else:
            requested_size = size
        flags = pygame.NOFRAME
    else:
        requested_size = size
        flags = pygame.RESIZABLE

    screen = pygame.display.set_mode(requested_size, flags, display=display_index)
    DISPLAY_MODE = mode
    DISPLAY_SIZE = screen.get_size()
    DISPLAY_INDEX = display_index
    return screen

# Initial display
change_display(DISPLAY_MODE, DISPLAY_SIZE)

clock = pygame.time.Clock()
music = MusicPlaylist()

game = Game(music)
running = True
music_started = False

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == music.ended_event:
            music.play_next()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                next_mode = "windowed" if DISPLAY_MODE == "fullscreen" else "fullscreen"
                change_display(next_mode, DISPLAY_SIZE, DISPLAY_INDEX)
                game.display_mode = DISPLAY_MODE
                game.display_index = DISPLAY_INDEX
                game.display_size = DISPLAY_SIZE
                game.settings_screen.sync(DISPLAY_MODE, DISPLAY_SIZE, DISPLAY_INDEX)
        elif event.type == pygame.VIDEORESIZE and DISPLAY_MODE == "windowed":
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE, display=DISPLAY_INDEX)
            DISPLAY_SIZE = screen.get_size()
            game.display_size = DISPLAY_SIZE
            game.settings_screen.sync(DISPLAY_MODE, DISPLAY_SIZE, DISPLAY_INDEX)
        elif event.type == pygame.MOUSEWHEEL and game.state == "settings":
            game.settings_screen.handle_scroll(event.y)

    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()[0]

    game.update(keys, mouse_pos, mouse_click, screen)
    if game.exit_requested:
        running = False
        break

    if game.display_request is not None:
        requested_mode, requested_size, requested_display = game.display_request
        game.display_request = None
        change_display(requested_mode, requested_size, requested_display)
        game.display_mode = DISPLAY_MODE
        game.display_index = DISPLAY_INDEX
        game.display_size = DISPLAY_SIZE
        game.settings_screen.sync(DISPLAY_MODE, DISPLAY_SIZE, DISPLAY_INDEX)

    # 🎨 Game handles ALL rendering
    game.draw(screen, mouse_pos)

    pygame.display.flip()

    # Let the first menu frame reach the display before starting its music.
    if not music_started and game.state == "menu":
        music.start()
        music_started = True

pygame.quit()

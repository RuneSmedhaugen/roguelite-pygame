import os
import sys
from pathlib import Path

import pygame
from core.assets import asset_path
from singleplayer.game import SinglePlayerGame
from core.music import MusicPlaylist
from core.startup import preload_startup_assets
from core.sound_effects import SoundEffects
from core.user_settings import load_settings, save_settings
from ui.intro import play_startup_intro
from ui.loading import draw_startup_loading

# Keep relative asset paths working when launched from a desktop shortcut.
APP_ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
os.chdir(APP_ROOT)

pygame.init()
pygame.display.set_caption("SPP")


user_settings = load_settings()
DISPLAY_MODE = user_settings["display_mode"]
DISPLAY_SIZE = tuple(user_settings["resolution"])
DISPLAY_INDEX = user_settings["display_index"]

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
try:
    change_display(DISPLAY_MODE, DISPLAY_SIZE, DISPLAY_INDEX)
except pygame.error:
    # The saved monitor may have been disconnected or the mode may no longer
    # be supported. Fall back to the primary display in a safe window.
    change_display("windowed", (1280, 720), 0)

clock = pygame.time.Clock()
music = MusicPlaylist()
music.set_audio_levels(**user_settings["audio_levels"])
sound_effects = SoundEffects(
    master=user_settings["audio_levels"]["master"],
    effects=user_settings["audio_levels"]["effects"],
)

screen.fill((5, 5, 12))
pygame.display.flip()
mascot = pygame.image.load(str(asset_path("sprites", "hammy.png"))).convert_alpha()
pygame.display.set_icon(pygame.transform.smoothscale(mascot, (64, 64)))
sound_effects.preload("Loud-male-scream-sound-effect.mp3")
sound_effects.preload("soundscrate-dropped-glass-1.mp3")
play_startup_intro(screen, mascot, clock, sound_effects)
audio_settings_dirty = False


def apply_audio_levels(**levels):
    global audio_settings_dirty
    music.set_audio_levels(**levels)
    sound_effects.set_audio_levels(**levels)
    user_settings["audio_levels"] = music.audio_levels
    audio_settings_dirty = True


def report_startup_progress(progress, message):
    draw_startup_loading(screen, progress, message)
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit(0)


preload_startup_assets(screen, music, sound_effects, report_startup_progress)

game = SinglePlayerGame(
    music,
    DISPLAY_MODE,
    DISPLAY_SIZE,
    DISPLAY_INDEX,
    sound_effects=sound_effects,
    on_audio_change=apply_audio_levels,
)
game.display_mode = DISPLAY_MODE
game.display_size = DISPLAY_SIZE
game.display_index = DISPLAY_INDEX
game.settings_screen.on_audio_change = apply_audio_levels
running = True
music_started = False

while running:
    clock.tick(60)

    for event in pygame.event.get():
        game.handle_event(event)
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
                user_settings.update(display_mode=DISPLAY_MODE, resolution=list(DISPLAY_SIZE), display_index=DISPLAY_INDEX)
                save_settings(user_settings)
        elif event.type == pygame.VIDEORESIZE and DISPLAY_MODE == "windowed":
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE, display=DISPLAY_INDEX)
            DISPLAY_SIZE = screen.get_size()
            game.display_size = DISPLAY_SIZE
            game.settings_screen.sync(DISPLAY_MODE, DISPLAY_SIZE, DISPLAY_INDEX)
            user_settings.update(display_mode=DISPLAY_MODE, resolution=list(DISPLAY_SIZE), display_index=DISPLAY_INDEX)
            save_settings(user_settings)
        elif event.type == pygame.MOUSEWHEEL:
            if game.state == "settings":
                game.settings_screen.handle_scroll(event.y)
            elif game.state == "achievements":
                game.handle_achievement_scroll(event.y, screen)
            elif game.state in ("game_over", "game_win"):
                game.handle_game_over_scroll(event.y, pygame.mouse.get_pos(), screen)

    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()[0]

    game.update(keys, mouse_pos, mouse_click, screen)
    if audio_settings_dirty and not mouse_click:
        save_settings(user_settings)
        audio_settings_dirty = False
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
        user_settings.update(display_mode=DISPLAY_MODE, resolution=list(DISPLAY_SIZE), display_index=DISPLAY_INDEX)
        save_settings(user_settings)

    # 🎨 Game handles ALL rendering
    game.draw(screen, mouse_pos)

    pygame.display.flip()

    # Let the first menu frame reach the display before starting its music.
    if not music_started and game.state == "menu":
        music.start()
        music_started = True

pygame.quit()

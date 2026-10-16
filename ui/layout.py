"""Resolution-aware sizing helpers for the directly rendered UI."""

import pygame


REFERENCE_SIZE = (800, 600)


def ui_scale(screen):
    width, height = screen.get_size()
    return max(0.65, min(width / REFERENCE_SIZE[0], height / REFERENCE_SIZE[1], 2.4))


def scaled(screen, value):
    return max(1, round(value * ui_scale(screen)))


def font(screen, base_size, bold=False):
    return pygame.font.SysFont(None, scaled(screen, base_size), bold=bold)


def menu_buttons(screen):
    width, height = screen.get_size()
    button_width = min(scaled(screen, 240), int(width * 0.72))
    button_height = scaled(screen, 64)
    gap = scaled(screen, 22)
    total_height = button_height * 3 + gap * 2
    top = round(height * 0.60 - total_height / 2)
    left = (width - button_width) // 2
    return [
        pygame.Rect(left, top + i * (button_height + gap), button_width, button_height)
        for i in range(3)
    ]


def settings_layout(screen):
    width, height = screen.get_size()
    margin = scaled(screen, 20)
    panel_width = min(scaled(screen, 560), width - 2 * margin)
    panel_height = min(scaled(screen, 540), height - 2 * margin)
    panel = pygame.Rect(0, 0, panel_width, panel_height)
    panel.center = (width // 2, height // 2)

    inner = scaled(screen, 32)
    row_height = scaled(screen, 42)
    row_width = panel.width - 2 * inner
    mode = pygame.Rect(panel.left + inner, panel.top + scaled(screen, 100), row_width, row_height)
    monitor = pygame.Rect(panel.left + inner, panel.top + scaled(screen, 162), row_width, row_height)
    resolution = pygame.Rect(panel.left + inner, panel.top + scaled(screen, 224), row_width, row_height)
    slider_height = scaled(screen, 28)
    master_volume = pygame.Rect(panel.left + inner, panel.top + scaled(screen, 310), row_width, slider_height)
    music_volume = pygame.Rect(panel.left + inner, panel.top + scaled(screen, 360), row_width, slider_height)
    effects_volume = pygame.Rect(panel.left + inner, panel.top + scaled(screen, 410), row_width, slider_height)
    button_width = scaled(screen, 150)
    button_height = scaled(screen, 42)
    button_y = panel.bottom - scaled(screen, 60)
    back = pygame.Rect(panel.left + inner, button_y, button_width, button_height)
    apply = pygame.Rect(panel.right - inner - button_width, button_y, button_width, button_height)
    return panel, mode, monitor, resolution, master_volume, music_volume, effects_volume, back, apply


def select_back_button(screen):
    return pygame.Rect(
        scaled(screen, 24),
        scaled(screen, 20),
        scaled(screen, 160),
        scaled(screen, 44),
    )


def selection_confirm_buttons(screen):
    width, height = screen.get_size()
    scale = ui_scale(screen)
    modal_width = min(scaled(screen, 500), width - scaled(screen, 40))
    modal_height = min(scaled(screen, 250), height - scaled(screen, 40))
    modal = pygame.Rect(0, 0, modal_width, modal_height)
    modal.center = (width // 2, height // 2)

    button_width = min(scaled(screen, 190), (modal_width - scaled(screen, 56)) // 2)
    button_height = scaled(screen, 48)
    gap = scaled(screen, 16)
    total_width = button_width * 2 + gap
    first_x = modal.centerx - total_width // 2
    button_y = modal.bottom - scaled(screen, 72)
    start = pygame.Rect(first_x, button_y, button_width, button_height)
    back = pygame.Rect(first_x + button_width + gap, button_y, button_width, button_height)
    return modal, start, back


def pause_layout(screen):
    width, height = screen.get_size()
    margin = scaled(screen, 18)
    button_size = scaled(screen, 42)
    pause_button = pygame.Rect(width - margin - button_size, margin, button_size, button_size)

    modal_width = min(scaled(screen, 420), width - 2 * margin)
    modal_height = min(scaled(screen, 330), height - 2 * margin)
    modal = pygame.Rect(0, 0, modal_width, modal_height)
    modal.center = (width // 2, height // 2)

    close_size = scaled(screen, 34)
    close = pygame.Rect(modal.right - scaled(screen, 16) - close_size, modal.top + scaled(screen, 14), close_size, close_size)
    button_width = min(scaled(screen, 280), modal.width - scaled(screen, 56))
    button_height = scaled(screen, 46)
    gap = scaled(screen, 14)
    buttons_top = modal.top + scaled(screen, 100)
    first_x = modal.centerx - button_width // 2
    continue_button = pygame.Rect(first_x, buttons_top, button_width, button_height)
    settings_button = pygame.Rect(first_x, buttons_top + button_height + gap, button_width, button_height)
    menu_button = pygame.Rect(first_x, buttons_top + 2 * (button_height + gap), button_width, button_height)
    return pause_button, modal, continue_button, settings_button, menu_button, close

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
    button_width = min(scaled(screen, 280), int(width * 0.72))
    button_height = scaled(screen, 48)
    gap = scaled(screen, 9)
    total_height = button_height * 6 + gap * 5
    top = round(height * 0.58 - total_height / 2)
    left = (width - button_width) // 2
    return [
        pygame.Rect(left, top + i * (button_height + gap), button_width, button_height)
        for i in range(6)
    ]


def achievements_layout(screen, item_count=0):
    width, height = screen.get_size()
    margin = scaled(screen, 22)
    tab_y = scaled(screen, 100)
    tab_height = scaled(screen, 34)
    filter_widths = (scaled(screen, 82), scaled(screen, 112), scaled(screen, 112))
    filter_gap = scaled(screen, 8)
    filters = {}
    left = margin
    for name, button_width in zip(("all", "classic", "endless"), filter_widths):
        filters[name] = pygame.Rect(left, tab_y, button_width, tab_height)
        left += button_width + filter_gap

    reset_width = scaled(screen, 138)
    reset = pygame.Rect(width - margin - reset_width, tab_y, reset_width, tab_height)
    back = pygame.Rect(margin, height - scaled(screen, 58), scaled(screen, 140), scaled(screen, 40))
    grid = pygame.Rect(
        margin,
        tab_y + tab_height + scaled(screen, 14),
        width - margin * 2,
        max(scaled(screen, 40), back.top - (tab_y + tab_height + scaled(screen, 26))),
    )
    columns = 4 if width >= 700 else (2 if width >= 420 else 1)
    gap = scaled(screen, 10)
    tile_width = (grid.width - gap * (columns - 1)) // columns
    tile_height = scaled(screen, 112)
    row_pitch = tile_height + gap
    visible_rows = max(1, (grid.height + gap) // row_pitch)
    total_rows = (item_count + columns - 1) // columns
    return {
        "filters": filters,
        "reset": reset,
        "back": back,
        "grid": grid,
        "columns": columns,
        "gap": gap,
        "tile_width": tile_width,
        "tile_height": tile_height,
        "row_pitch": row_pitch,
        "visible_rows": visible_rows,
        "max_scroll": max(0, total_rows - visible_rows),
    }


def achievement_reset_layout(screen):
    width, height = screen.get_size()
    modal_width = min(scaled(screen, 450), width - scaled(screen, 32))
    modal_height = scaled(screen, 190)
    modal = pygame.Rect(0, 0, modal_width, modal_height)
    modal.center = (width // 2, height // 2)
    button_width = min(scaled(screen, 160), (modal.width - scaled(screen, 48)) // 2)
    button_height = scaled(screen, 42)
    gap = scaled(screen, 12)
    first_x = modal.centerx - (button_width * 2 + gap) // 2
    button_y = modal.bottom - scaled(screen, 60)
    return (
        modal,
        pygame.Rect(first_x, button_y, button_width, button_height),
        pygame.Rect(first_x + button_width + gap, button_y, button_width, button_height),
    )


def mode_select_buttons(screen):
    width, height = screen.get_size()
    button_width = min(scaled(screen, 360), int(width * 0.78))
    button_height = scaled(screen, 72)
    gap = scaled(screen, 22)
    left = (width - button_width) // 2
    top = round(height * 0.47)
    return (
        pygame.Rect(left, top, button_width, button_height),
        pygame.Rect(left, top + button_height + gap, button_width, button_height),
        pygame.Rect(left, top + (button_height + gap) * 2, button_width, scaled(screen, 48)),
    )


def feedback_layout(screen):
    width, height = screen.get_size()
    margin = scaled(screen, 24)
    panel_width = min(scaled(screen, 620), width - 2 * margin)
    panel_height = min(scaled(screen, 500), height - 2 * margin)
    panel = pygame.Rect(0, 0, panel_width, panel_height)
    panel.center = (width // 2, height // 2)
    inner = scaled(screen, 28)
    button_height = scaled(screen, 44)
    button_width = min(scaled(screen, 210), (panel.width - inner * 2 - scaled(screen, 16)) // 2)
    buttons_y = panel.bottom - inner - button_height
    first_x = panel.centerx - (button_width * 2 + scaled(screen, 16)) // 2
    first = pygame.Rect(first_x, buttons_y, button_width, button_height)
    second = pygame.Rect(first.right + scaled(screen, 16), buttons_y, button_width, button_height)
    field_width = panel.width - inner * 2
    title_rect = pygame.Rect(panel.left + inner, panel.top + scaled(screen, 100), field_width, scaled(screen, 42))
    severity_rect = pygame.Rect(panel.left + inner, panel.top + scaled(screen, 170), field_width, scaled(screen, 42))
    message_top = panel.top + scaled(screen, 240)
    content = pygame.Rect(panel.left + inner, message_top, field_width, max(scaled(screen, 54), buttons_y - message_top - scaled(screen, 12)))
    option_height = scaled(screen, 34)
    severity_options = [
        pygame.Rect(severity_rect.left, severity_rect.bottom + scaled(screen, 4) + i * option_height, severity_rect.width, option_height)
        for i in range(3)
    ]
    return panel, title_rect, severity_rect, severity_options, content, first, second


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


def game_over_layout(screen, show_achievements=False):
    width, height = screen.get_size()
    margin = scaled(screen, 28)
    button_width = min(scaled(screen, 220), (width - margin * 3) // 2)
    button_height = scaled(screen, 48)
    button_y = height - margin - button_height
    gap = scaled(screen, 18)
    total_width = button_width * 2 + gap
    left = (width - total_width) // 2
    retry = pygame.Rect(left, button_y, button_width, button_height)
    menu = pygame.Rect(left + button_width + gap, button_y, button_width, button_height)

    content_top = round(height * (0.42 if show_achievements else 0.29))
    content_bottom = button_y - scaled(screen, 18)
    content_height = max(scaled(screen, 80), content_bottom - content_top)
    content_width = width - margin * 2
    gap = scaled(screen, 14)
    battle_width = round((content_width - gap) * 0.58)
    battles = pygame.Rect(margin, content_top, battle_width, content_height)
    upgrades = pygame.Rect(battles.right + gap, content_top, content_width - battle_width - gap, content_height)
    return retry, menu, battles, upgrades


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
    feedback_button = pygame.Rect(pause_button.left - scaled(screen, 112) - scaled(screen, 8), margin + scaled(screen, 2), scaled(screen, 112), scaled(screen, 38))

    modal_width = min(scaled(screen, 420), width - 2 * margin)
    modal_height = min(scaled(screen, 350), height - 2 * margin)
    modal = pygame.Rect(0, 0, modal_width, modal_height)
    modal.center = (width // 2, height // 2)

    close_size = scaled(screen, 34)
    close = pygame.Rect(modal.right - scaled(screen, 16) - close_size, modal.top + scaled(screen, 14), close_size, close_size)
    button_width = min(scaled(screen, 280), modal.width - scaled(screen, 56))
    button_height = scaled(screen, 42)
    gap = scaled(screen, 10)
    buttons_top = modal.top + scaled(screen, 88)
    first_x = modal.centerx - button_width // 2
    continue_button = pygame.Rect(first_x, buttons_top, button_width, button_height)
    settings_button = pygame.Rect(first_x, buttons_top + button_height + gap, button_width, button_height)
    feedback_modal_button = pygame.Rect(first_x, buttons_top + 2 * (button_height + gap), button_width, button_height)
    menu_button = pygame.Rect(first_x, buttons_top + 3 * (button_height + gap), button_width, button_height)
    return pause_button, feedback_button, modal, continue_button, settings_button, feedback_modal_button, menu_button, close


def global_feedback_button(screen):
    width, _ = screen.get_size()
    margin = scaled(screen, 18)
    button_width = scaled(screen, 112)
    button_height = scaled(screen, 38)
    pause_button, *_ = pause_layout(screen)
    left = pause_button.left - button_width - scaled(screen, 8)
    return pygame.Rect(max(margin, min(left, width - margin - button_width)), margin + scaled(screen, 2), button_width, button_height)

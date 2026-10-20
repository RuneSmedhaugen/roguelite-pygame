"""Drawing helpers for the startup loading screen."""

import pygame

from ui.layout import font, scaled


def draw_startup_loading(screen, progress, message):
    width, height = screen.get_size()
    progress = max(0.0, min(1.0, progress))
    center_x = width // 2

    screen.fill((20, 20, 30))

    title_font = font(screen, 48, bold=True)
    title = title_font.render("SMALL PUNCH PUPPIES", True, (255, 231, 174))
    screen.blit(title, title.get_rect(center=(center_x, round(height * 0.40))))

    subtitle_font = font(screen, 20)
    subtitle = subtitle_font.render("Getting the tiny paws ready...", True, (190, 199, 218))
    screen.blit(subtitle, subtitle.get_rect(center=(center_x, round(height * 0.49))))

    bar_width = min(round(width * 0.52), scaled(screen, 560))
    bar_height = max(12, scaled(screen, 20))
    bar = pygame.Rect(center_x - bar_width // 2, round(height * 0.57), bar_width, bar_height)
    pygame.draw.rect(screen, (52, 55, 69), bar, border_radius=bar_height // 2)

    fill_width = round(bar_width * progress)
    if fill_width > 0:
        fill = pygame.Rect(bar.left, bar.top, fill_width, bar_height)
        pygame.draw.rect(screen, (226, 161, 76), fill, border_radius=bar_height // 2)

    status_font = font(screen, 17)
    status = status_font.render(message, True, (218, 221, 232))
    screen.blit(status, status.get_rect(center=(center_x, bar.bottom + scaled(screen, 28))))

    percent = font(screen, 15, bold=True).render(f"{round(progress * 100)}%", True, (255, 231, 174))
    screen.blit(percent, percent.get_rect(center=(center_x, bar.bottom + scaled(screen, 58))))

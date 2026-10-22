"""Achievement collection and notification rendering."""

import pygame

from ui.draw import get_sprite
from ui.layout import achievement_reset_layout, achievements_layout, font, scaled


def _wrap(text, text_font, max_width):
    lines = []
    line = ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if line and text_font.size(candidate)[0] > max_width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def _draw_badge(screen, achievement, rect, unlocked, sprite_size):
    color = achievement["color"] if unlocked else (61, 67, 81)
    edge = tuple(min(255, value + 34) for value in achievement["color"]) if unlocked else (103, 111, 128)
    pygame.draw.rect(screen, color, rect, border_radius=scaled(screen, 7))
    pygame.draw.rect(screen, edge, rect, width=max(1, scaled(screen, 2)),
                     border_radius=scaled(screen, 7))
    inner = pygame.Rect(0, 0, sprite_size, sprite_size)
    inner.center = rect.center
    pygame.draw.rect(screen, (25, 28, 39), inner, border_radius=scaled(screen, 5))
    if achievement.get("sprite"):
        sprite = get_sprite(achievement["sprite"], (sprite_size - scaled(screen, 6),) * 2)
        if not unlocked:
            sprite = pygame.transform.grayscale(sprite).copy()
            sprite.set_alpha(145)
        screen.blit(sprite, sprite.get_rect(center=inner.center))
def draw_achievements_screen(screen, game, mouse_pos):
    screen.fill((17, 20, 30))
    store = game.achievement_store
    all_entries = store.filtered("all")
    entries = store.filtered(game.achievement_filter)
    title = font(screen, 48, bold=True).render("ACHIEVEMENTS", True, (247, 225, 160))
    screen.blit(title, title.get_rect(center=(screen.get_width() // 2, scaled(screen, 37))))
    progress = font(screen, 18).render(
        f"{len(store.unlocked)} / {len(all_entries)} unlocked", True, (186, 197, 216))
    screen.blit(progress, progress.get_rect(center=(screen.get_width() // 2, scaled(screen, 72))))

    layout = achievements_layout(screen, len(entries))
    counts = {mode: len(store.filtered(mode)) for mode in ("all", "classic", "endless")}
    for mode, rect in layout["filters"].items():
        selected = mode == game.achievement_filter
        pygame.draw.rect(screen, (91, 105, 137) if selected else (44, 50, 67),
                         rect, border_radius=scaled(screen, 6))
        label = font(screen, 15, bold=True).render(
            f"{mode.upper()} ({counts[mode]})", True, (240, 243, 250))
        screen.blit(label, label.get_rect(center=rect.center))

    reset_rect = layout["reset"]
    pygame.draw.rect(screen, (105, 57, 59), reset_rect, border_radius=scaled(screen, 6))
    label = font(screen, 15, bold=True).render("RESET ALL", True, (255, 236, 230))
    screen.blit(label, label.get_rect(center=reset_rect.center))
    back_rect = layout["back"]
    pygame.draw.rect(screen, (62, 72, 105), back_rect, border_radius=scaled(screen, 7))
    label = font(screen, 20, bold=True).render("BACK", True, (255, 255, 255))
    screen.blit(label, label.get_rect(center=back_rect.center))

    start_index = game.achievement_scroll * layout["columns"]
    end_index = start_index + layout["visible_rows"] * layout["columns"]
    old_clip = screen.get_clip()
    screen.set_clip(layout["grid"])
    badge_size = scaled(screen, 48)
    for offset, achievement in enumerate(entries[start_index:end_index]):
        index = start_index + offset
        row, column = divmod(index, layout["columns"])
        card = pygame.Rect(
            layout["grid"].left + column * (layout["tile_width"] + layout["gap"]),
            layout["grid"].top + (row - game.achievement_scroll) * layout["row_pitch"],
            layout["tile_width"], layout["tile_height"])
        unlocked = achievement["id"] in store.unlocked
        pygame.draw.rect(screen, (34, 40, 54) if unlocked else (27, 31, 43),
                         card, border_radius=scaled(screen, 8))
        pygame.draw.rect(screen, achievement["color"] if unlocked else (63, 70, 87),
                         card, width=max(1, scaled(screen, 2)),
                         border_radius=scaled(screen, 8))

        badge = pygame.Rect(0, 0, badge_size, badge_size)
        badge.center = (card.centerx, card.top + scaled(screen, 30))
        _draw_badge(screen, achievement, badge, unlocked, badge_size - scaled(screen, 4))
        title_font = font(screen, 14, bold=True)
        title_lines = _wrap(achievement["name"], title_font, card.width - scaled(screen, 10))
        title_y = badge.bottom + scaled(screen, 4)
        for line_index, line in enumerate(title_lines[:2]):
            rendered = title_font.render(line, True, (246, 231, 191) if unlocked else (180, 187, 202))
            screen.blit(rendered, rendered.get_rect(
                center=(card.centerx, title_y + line_index * title_font.get_linesize())))
        detail_font = font(screen, 11)
        detail_lines = _wrap(achievement["description"], detail_font, card.width - scaled(screen, 12))
        detail_y = title_y + 2 * title_font.get_linesize()
        for line_index, line in enumerate(detail_lines[:2]):
            rendered = detail_font.render(line, True, (183, 193, 211) if unlocked else (125, 134, 151))
            screen.blit(rendered, rendered.get_rect(
                center=(card.centerx, detail_y + line_index * detail_font.get_linesize())))
    screen.set_clip(old_clip)

    if layout["max_scroll"]:
        hint = font(screen, 15).render(
            f"Scroll to browse  •  {game.achievement_scroll + 1}/{layout['max_scroll'] + 1}",
            True, (144, 154, 175))
        screen.blit(hint, hint.get_rect(
            midbottom=(screen.get_width() // 2, screen.get_height() - scaled(screen, 8))))

    if game.achievement_reset_confirm:
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        screen.blit(overlay, (0, 0))
        modal, confirm, cancel = achievement_reset_layout(screen)
        pygame.draw.rect(screen, (34, 39, 53), modal, border_radius=scaled(screen, 12))
        pygame.draw.rect(screen, (156, 86, 81), modal, width=max(1, scaled(screen, 2)),
                         border_radius=scaled(screen, 12))
        prompt = font(screen, 24, bold=True).render("Reset all achievements?", True, (255, 238, 227))
        screen.blit(prompt, prompt.get_rect(center=(modal.centerx, modal.top + scaled(screen, 44))))
        detail = font(screen, 16).render("This clears your saved unlocks.", True, (190, 197, 211))
        screen.blit(detail, detail.get_rect(center=(modal.centerx, modal.top + scaled(screen, 78))))
        for rect, text, color in (
            (confirm, "RESET", (142, 62, 61)),
            (cancel, "CANCEL", (73, 86, 112)),
        ):
            pygame.draw.rect(screen, color, rect, border_radius=scaled(screen, 7))
            label = font(screen, 18, bold=True).render(text, True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=rect.center))


def draw_achievement_toast(screen, achievement):
    width, height = screen.get_size()
    card = pygame.Rect(0, 0, min(scaled(screen, 470), width - scaled(screen, 28)), scaled(screen, 76))
    card.center = (width // 2, round(height * .24))
    pygame.draw.rect(screen, (28, 33, 46), card, border_radius=scaled(screen, 10))
    pygame.draw.rect(screen, achievement["color"], card, width=max(1, scaled(screen, 2)),
                     border_radius=scaled(screen, 10))
    icon_size = scaled(screen, 52)
    badge = pygame.Rect(card.left + scaled(screen, 10), card.centery - icon_size // 2,
                        icon_size, icon_size)
    _draw_badge(screen, achievement, badge, True, icon_size)
    left = badge.right + scaled(screen, 12)
    heading = font(screen, 14, bold=True).render("ACHIEVEMENT UNLOCKED", True, (229, 200, 125))
    screen.blit(heading, (left, card.top + scaled(screen, 10)))
    name_font = font(screen, 19, bold=True)
    max_width = card.right - left - scaled(screen, 12)
    while name_font.size(achievement["name"])[0] > max_width and name_font.get_height() > scaled(screen, 12):
        name_font = pygame.font.SysFont(None, name_font.get_height() - 1, bold=True)
    name = name_font.render(achievement["name"], True, (250, 245, 233))
    screen.blit(name, (left, card.top + scaled(screen, 37)))

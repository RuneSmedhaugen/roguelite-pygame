import math
import pygame
from ui.layout import feedback_layout, font, game_over_layout, menu_buttons, pause_layout, scaled, select_back_button, selection_confirm_buttons, ui_scale

# -------------------------
# SPRITE CACHE (NO LAG ZONE)
# -------------------------
SPRITE_CACHE = {}
SPRITE_SOURCE_CACHE = {}

def get_sprite(name, size=(120, 120)):
    key = (name, tuple(size))
    if key not in SPRITE_CACHE:
        if name not in SPRITE_SOURCE_CACHE:
            SPRITE_SOURCE_CACHE[name] = pygame.image.load(f"assets/sprites/{name}").convert_alpha()
        SPRITE_CACHE[key] = pygame.transform.smoothscale(SPRITE_SOURCE_CACHE[name], size)
    return SPRITE_CACHE[key]

def draw_menu(self, screen, menu_antics=None):
    screen.fill((20, 20, 30))
    if menu_antics is not None:
        menu_antics.draw(screen, pygame.time.get_ticks())

    # Keep the logo in one clean line and size it to the space above the menu.
    buttons = menu_buttons(screen)
    title_font = pygame.font.SysFont("arial", scaled(screen, 54), bold=True)
    title_text = "SMALL PUNCH PUPPIES"
    max_width = int(screen.get_width() * 0.9)
    while title_font.size(title_text)[0] > max_width and title_font.get_height() > scaled(screen, 20):
        title_font = pygame.font.SysFont("arial", title_font.get_height() - 1, bold=True)
    title = title_font.render(title_text, True, (255, 231, 174))
    title_y = round(screen.get_height() * 0.12)
    title_rect = title.get_rect(center=(screen.get_width() // 2, title_y + title.get_height() // 2))
    screen.blit(title_font.render(title_text, True, (12, 14, 22)), title_rect.move(0, scaled(screen, 3)))
    screen.blit(title, title_rect)

    tagline_font = pygame.font.SysFont("arial", scaled(screen, 18))
    tagline = tagline_font.render("TINY PAWS. HUGE BONKS.", True, (190, 199, 218))
    tagline_y = title_rect.bottom + scaled(screen, 8)
    available_bottom = buttons[0].top - scaled(screen, 12)
    tagline_rect = tagline.get_rect(center=(screen.get_width() // 2, tagline_y + tagline.get_height() // 2))
    if tagline_rect.bottom <= available_bottom:
        screen.blit(tagline, tagline_rect)

    alpha_text = "ALPHA  •  Bugs, balance issues & weird behaviour expected"
    alpha_font = pygame.font.SysFont("arial", scaled(screen, 17), bold=True)
    while alpha_font.size(alpha_text)[0] > screen.get_width() - scaled(screen, 28) and alpha_font.get_height() > 1:
        alpha_font = pygame.font.SysFont("arial", alpha_font.get_height() - 1, bold=True)
    alpha_note = alpha_font.render(alpha_text, True, (240, 214, 157))
    alpha_rect = alpha_note.get_rect(center=(screen.get_width() // 2, screen.get_height() - scaled(screen, 25)))
    alpha_panel = alpha_rect.inflate(scaled(screen, 24), scaled(screen, 12))
    pygame.draw.rect(screen, (35, 32, 31), alpha_panel, border_radius=scaled(screen, 8))
    screen.blit(alpha_note, alpha_rect)

    button_font = font(screen, 40)

    labels = (("PLAY", (60, 120, 200)), ("SETTINGS", (80, 80, 80)), ("FEEDBACK", (74, 105, 88)), ("EXIT GAME", (120, 55, 55)))
    for rect, (label, color) in zip(menu_buttons(screen), labels):
        pygame.draw.rect(screen, color, rect, border_radius=scaled(screen, 10))
        text = button_font.render(label, True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=rect.center))


def draw_feedback_screen(screen, state, kind, message, status=""):
    screen.fill((20, 20, 30))
    panel, content, first, second = feedback_layout(screen)
    pygame.draw.rect(screen, (34, 38, 53), panel, border_radius=scaled(screen, 14))
    pygame.draw.rect(screen, (86, 94, 119), panel, width=scaled(screen, 2), border_radius=scaled(screen, 14))
    title_font = font(screen, 42, bold=True)
    body_font = font(screen, 25)
    button_font = font(screen, 27, bold=True)
    title = "SEND FEEDBACK" if state == "feedback_type" else ("BUG REPORT" if kind == "bug_report" else "SUGGESTION")
    rendered_title = title_font.render(title, True, (245, 225, 151))
    screen.blit(rendered_title, rendered_title.get_rect(center=(panel.centerx, panel.top + scaled(screen, 52))))

    if state == "feedback_type":
        pygame.draw.rect(screen, (145, 69, 64), first, border_radius=scaled(screen, 9))
        pygame.draw.rect(screen, (71, 111, 86), second, border_radius=scaled(screen, 9))
        for rect, label in ((first, "BUG REPORT"), (second, "SUGGESTION")):
            text = button_font.render(label, True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=rect.center))
        hint = body_font.render("What would you like to send?", True, (215, 218, 228))
        screen.blit(hint, hint.get_rect(center=(panel.centerx, content.centery)))
        escape_hint = font(screen, 18).render("Press ESC to return to the main menu", True, (150, 157, 176))
        screen.blit(escape_hint, escape_hint.get_rect(center=(panel.centerx, panel.bottom - scaled(screen, 20))))
    else:
        pygame.draw.rect(screen, (16, 19, 28), content, border_radius=scaled(screen, 8))
        pygame.draw.rect(screen, (107, 116, 143), content, width=scaled(screen, 2), border_radius=scaled(screen, 8))
        margin = scaled(screen, 14)
        lines = message.splitlines() or [""]
        line_height = body_font.get_linesize()
        max_lines = max(1, (content.height - margin * 2) // line_height)
        visible = lines[-max_lines:]
        for index, line in enumerate(visible):
            # Wrap long lines to the available width.
            words = line.split(" ")
            wrapped, current = [], ""
            for word in words:
                trial = f"{current} {word}".strip()
                if current and body_font.size(trial)[0] > content.width - margin * 2:
                    wrapped.append(current)
                    current = word
                else:
                    current = trial
            wrapped.append(current)
            for row, text_line in enumerate(wrapped):
                y = content.top + margin + (index + row) * line_height
                if y + line_height <= content.bottom - margin:
                    screen.blit(body_font.render(text_line, True, (240, 240, 245)), (content.left + margin, y))
        if not message:
            hint = body_font.render("Write your message here...", True, (130, 136, 154))
            screen.blit(hint, (content.left + margin, content.top + margin))
        if status:
            status_color = (235, 144, 120) if "failed" in status.lower() or "could not" in status.lower() else (232, 210, 145)
            status_text = font(screen, 18).render(status, True, status_color)
            screen.blit(status_text, status_text.get_rect(center=(panel.centerx, first.top - scaled(screen, 14))))
        for rect, label, color in ((first, "SEND", (65, 125, 82)), (second, "CANCEL", (100, 68, 72))):
            pygame.draw.rect(screen, color, rect, border_radius=scaled(screen, 9))
            text = button_font.render(label, True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=rect.center))

# -------------------------
# TEXT WRAP (FIXED GLOBAL)
# -------------------------
def draw_text_wrapped(screen, text, font, x, y, max_width, color=(180,180,180)):
    words = text.split(" ")
    lines = []
    current = ""

    for word in words:
        test = current + word + " "
        if font.size(test)[0] > max_width:
            lines.append(current.rstrip())
            current = word + " "
        else:
            current = test

    lines.append(current)

    for i, line in enumerate(lines):
        rendered = font.render(line, True, color)
        screen.blit(rendered, (x, y + i * font.get_linesize()))


# -------------------------
# ROUND
# -------------------------
def draw_round(screen, round_number):
    round_font = font(screen, 40)
    text = round_font.render(f"Round {round_number}", True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=(screen.get_width() // 2, scaled(screen, 34))))


# -------------------------
# UPGRADES
# -------------------------
def draw_upgrades(screen, upgrades, result=None):
    screen.fill((15, 15, 25))
    text_font = font(screen, 40)
    rects = []

    if result is not None:
        won = result == "player"
        headline = font(screen, 72).render(
            "YOU WIN!" if won else "YOU LOSE!",
            True,
            (255, 220, 80) if won else (255, 85, 85),
        )
        screen.blit(headline, headline.get_rect(center=(screen.get_width() // 2, round(screen.get_height() * 0.16))))
        prompt = font(screen, 28).render("Choose an upgrade to continue", True, (205, 210, 225))
        screen.blit(prompt, prompt.get_rect(center=(screen.get_width() // 2, round(screen.get_height() * 0.27))))

    margin = scaled(screen, 40)
    card_width = min(scaled(screen, 560), screen.get_width() - margin * 2)
    card_height = scaled(screen, 70)
    gap = scaled(screen, 20)
    total_height = len(upgrades) * card_height + max(0, len(upgrades) - 1) * gap
    top = (screen.get_height() - total_height) // 2
    if result is not None:
        top = max(top, round(screen.get_height() * 0.34))

    for i, upg in enumerate(upgrades):

        rect = pygame.Rect((screen.get_width() - card_width) // 2, top + i * (card_height + gap), card_width, card_height)
        rects.append(rect)

        pygame.draw.rect(
            screen,
            (40, 40, 60),
            rect,
            border_radius=scaled(screen, 8)
        )

        text = text_font.render(f"{i+1}: {upg['name']}", True, (255, 255, 255))
        screen.blit(text, text.get_rect(midleft=(rect.left + scaled(screen, 20), rect.centery)))

    return rects


# -------------------------
# STATS PANEL (BATTLE)
# -------------------------
def draw_stats(screen, character, x, y):
    stats_font = font(screen, 22)
    title_font = font(screen, 32)

    panel_width = scaled(screen, 220)
    panel_height = scaled(screen, 190)
    padding = scaled(screen, 10)

    pygame.draw.rect(
        screen,
        (30, 30, 45),
        (x - padding, y - padding, panel_width, panel_height),
        border_radius=scaled(screen, 10)
    )

    name = getattr(character, "name", "Unknown")
    title = title_font.render(name, True, (255, 255, 255))
    screen.blit(title, (x, y))

    stats = [
        f"HP: {int(character.hp)}/{int(character.max_hp)}",
        f"ATK: {character.atk_min}-{character.atk_max}",
        f"SPD: {character.attack_speed:.2f}",
        f"CRIT: {int(character.crit * 100)}%",
        f"DODGE: {int(character.dodge * 100)}%",
        f"LS: {int(character.lifesteal * 100)}%",
        f"ARMOR: {character.armor}",
    ]

    for i, line in enumerate(stats):
        text = stats_font.render(line, True, (220, 220, 220))
        screen.blit(text, (x, y + scaled(screen, 30) + i * scaled(screen, 19)))


def draw_game_over(screen, game, mouse_pos):
    screen.fill((15, 15, 25))
    title = font(screen, 64, bold=True).render("RUN OVER", True, (255, 102, 102))
    screen.blit(title, title.get_rect(center=(screen.get_width() // 2, round(screen.get_height() * 0.095))))

    victories = sum(battle["result"] == "Victory" for battle in game.battle_history)
    summary_text = (
        f"{game.run_character or 'Your fighter'}  •  {len(game.battle_history)} battles  •  "
        f"{victories} victories  •  {len(game.upgrade_history)} upgrades"
    )
    summary = font(screen, 25).render(summary_text, True, (205, 211, 229))
    screen.blit(summary, summary.get_rect(center=(screen.get_width() // 2, round(screen.get_height() * 0.20))))

    retry_button, menu_button, battles_rect, upgrades_rect = game_over_layout(screen)
    panel_color = (29, 34, 49)
    pygame.draw.rect(screen, panel_color, battles_rect, border_radius=scaled(screen, 10))
    pygame.draw.rect(screen, panel_color, upgrades_rect, border_radius=scaled(screen, 10))
    heading_font = font(screen, 25, bold=True)
    row_font = font(screen, 20)
    screen.blit(heading_font.render("BATTLES", True, (236, 214, 159)), (battles_rect.left + scaled(screen, 12), battles_rect.top + scaled(screen, 10)))
    screen.blit(heading_font.render("UPGRADES", True, (166, 207, 238)), (upgrades_rect.left + scaled(screen, 12), upgrades_rect.top + scaled(screen, 10)))

    row_height = scaled(screen, 28)
    first_row_y = battles_rect.top + scaled(screen, 42)
    visible_rows = max(1, (battles_rect.height - scaled(screen, 52)) // row_height)
    screen.set_clip(battles_rect)
    battle_rows = game.battle_history[game.game_over_battle_scroll:game.game_over_battle_scroll + visible_rows]
    for index, battle in enumerate(battle_rows):
        won = battle["result"] == "Victory"
        result_color = (135, 220, 162) if won else (239, 126, 126)
        result_text = "W" if won else "L"
        details = (
            f"R{battle['round']} [{result_text}] {battle['opponent']}  "
            f"HP {int(battle['player_hp'])}/{int(battle['player_max_hp'])}  "
            f"Lives {battle['lives']}"
        )
        row_y = first_row_y + index * row_height
        screen.blit(row_font.render(details, True, result_color), (battles_rect.left + scaled(screen, 12), row_y))
    screen.set_clip(None)

    screen.set_clip(upgrades_rect)
    upgrade_rows = game.upgrade_history[game.game_over_upgrade_scroll:game.game_over_upgrade_scroll + visible_rows]
    if not game.upgrade_history:
        empty = row_font.render("No upgrades chosen", True, (160, 166, 182))
        screen.blit(empty, (upgrades_rect.left + scaled(screen, 12), first_row_y))
    for index, upgrade in enumerate(upgrade_rows):
        text = f"R{upgrade['round']}  {upgrade['name']}"
        screen.blit(row_font.render(text, True, (218, 225, 239)), (upgrades_rect.left + scaled(screen, 12), first_row_y + index * row_height))
    screen.set_clip(None)

    if len(game.battle_history) > visible_rows:
        hint = font(screen, 16).render("Scroll to see more", True, (143, 151, 173))
        screen.blit(hint, (battles_rect.right - hint.get_width() - scaled(screen, 10), battles_rect.bottom - hint.get_height() - scaled(screen, 5)))
    if len(game.upgrade_history) > visible_rows:
        hint = font(screen, 16).render("Scroll to see more", True, (143, 151, 173))
        screen.blit(hint, (upgrades_rect.right - hint.get_width() - scaled(screen, 10), upgrades_rect.bottom - hint.get_height() - scaled(screen, 5)))

    for rect, label, color in (
        (retry_button, "RETRY", (55, 119, 91)),
        (menu_button, "MAIN MENU", (83, 91, 117)),
    ):
        hovered = rect.collidepoint(mouse_pos)
        button_color = tuple(min(255, channel + 18) for channel in color) if hovered else color
        pygame.draw.rect(screen, button_color, rect, border_radius=scaled(screen, 8))
        text = font(screen, 25, bold=True).render(label, True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=rect.center))


def draw_battle_outcome_labels(screen, winner):
    width, height = screen.get_size()
    midpoint = width // 2
    winner_center = midpoint // 2 if winner == "player" else midpoint + (width - midpoint) // 2
    loser_center = midpoint + (width - midpoint) // 2 if winner == "player" else midpoint // 2
    victory = font(screen, 68, bold=True).render("VICTORY!", True, (255, 225, 135))
    defeat = font(screen, 54, bold=True).render("DEFEATED", True, (203, 207, 214))
    screen.blit(victory, victory.get_rect(center=(winner_center, round(height * 0.13))))
    screen.blit(defeat, defeat.get_rect(center=(loser_center, round(height * 0.13))))


def draw_pause_button(screen, mouse_pos):
    button, *_ = pause_layout(screen)
    hovered = button.collidepoint(mouse_pos)
    color = (91, 106, 148) if hovered else (45, 52, 76)
    pygame.draw.rect(screen, color, button, border_radius=scaled(screen, 8))
    bar_width = scaled(screen, 5)
    bar_height = scaled(screen, 18)
    gap = scaled(screen, 5)
    first_x = button.centerx - gap // 2 - bar_width
    for x in (first_x, first_x + bar_width + gap):
        pygame.draw.rect(
            screen,
            (245, 245, 255),
            (x, button.centery - bar_height // 2, bar_width, bar_height),
            border_radius=scaled(screen, 2),
        )


def draw_life_runes(screen, lives, max_lives=5):
    label_font = font(screen, 20, bold=True)
    label = label_font.render("LIVES", True, (225, 229, 239))
    x = scaled(screen, 22)
    y = scaled(screen, 18)
    icon_size = scaled(screen, 23)
    gap = scaled(screen, 6)
    screen.blit(label, (x, y + (icon_size - label.get_height()) // 2))
    x += label.get_width() + scaled(screen, 8)

    for index in range(max_lives):
        active = index < lives
        points = [
            (x + icon_size // 2, y),
            (x + icon_size - 1, y + icon_size // 4),
            (x + icon_size * 4 // 5, y + icon_size * 3 // 4),
            (x + icon_size // 2, y + icon_size - 1),
            (x + icon_size // 5, y + icon_size * 3 // 4),
            (x, y + icon_size // 4),
        ]
        fill = (147, 91, 33) if active else (35, 42, 57)
        edge = (255, 211, 105) if active else (91, 103, 127)
        rune = (255, 240, 177) if active else (69, 80, 103)
        pygame.draw.polygon(screen, fill, points)
        pygame.draw.polygon(screen, edge, points, width=max(1, scaled(screen, 2)))

        center_x = x + icon_size // 2
        if active:
            pygame.draw.line(
                screen,
                rune,
                (center_x, y + scaled(screen, 5)),
                (center_x, y + icon_size - scaled(screen, 5)),
                max(1, scaled(screen, 2)),
            )
            pygame.draw.line(
                screen,
                rune,
                (center_x - scaled(screen, 4), y + icon_size // 2),
                (center_x + scaled(screen, 4), y + icon_size // 2),
                max(1, scaled(screen, 2)),
            )
        x += icon_size + gap


def draw_pause_menu(screen, mouse_pos):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((5, 8, 16, 165))
    screen.blit(overlay, (0, 0))

    _, modal, continue_button, settings_button, menu_button, close_button = pause_layout(screen)
    pygame.draw.rect(screen, (31, 36, 53), modal, border_radius=scaled(screen, 16))
    pygame.draw.rect(screen, (105, 122, 166), modal, width=scaled(screen, 2), border_radius=scaled(screen, 16))

    title = font(screen, 48).render("PAUSED", True, (248, 242, 220))
    screen.blit(title, title.get_rect(center=(modal.centerx, modal.top + scaled(screen, 55))))

    for rect, label, base_color in (
        (continue_button, "CONTINUE", (55, 119, 91)),
        (settings_button, "SETTINGS", (62, 78, 116)),
        (menu_button, "MAIN MENU", (112, 60, 65)),
    ):
        hovered = rect.collidepoint(mouse_pos)
        color = tuple(min(255, channel + 18) for channel in base_color) if hovered else base_color
        pygame.draw.rect(screen, color, rect, border_radius=scaled(screen, 8))
        label_surface = font(screen, 25).render(label, True, (255, 255, 255))
        screen.blit(label_surface, label_surface.get_rect(center=rect.center))

    close_hovered = close_button.collidepoint(mouse_pos)
    pygame.draw.rect(
        screen,
        (112, 64, 70) if close_hovered else (66, 51, 64),
        close_button,
        border_radius=scaled(screen, 7),
    )
    x_font = font(screen, 30, bold=True)
    x_text = x_font.render("×", True, (255, 255, 255))
    screen.blit(x_text, x_text.get_rect(center=close_button.center))


# -------------------------
# CHARACTER SELECT (CLEAN + “CSS FEEL”)
# -------------------------
def draw_character_select(screen, characters, selected_index, mouse_pos, dry_run=False, confirmation_index=None):
    if not dry_run:
        screen.fill((15, 15, 25))
        back_rect = select_back_button(screen)
        pygame.draw.rect(screen, (62, 72, 105), back_rect, border_radius=scaled(screen, 8))
        back_text = font(screen, 22).render("MAIN MENU", True, (255, 255, 255))
        screen.blit(back_text, back_text.get_rect(center=back_rect.center))

    width, height = screen.get_size()
    scale = ui_scale(screen)
    margin = scaled(screen, 28)
    slot_pitch = min(scaled(screen, 150), (width - margin * 2) // max(1, len(characters)))
    row_width = slot_pitch * len(characters)
    start_x = (width - row_width) // 2
    row_top = round(height * 0.12)
    hit_height = scaled(screen, 176)
    name_font_size = scaled(screen, 28)
    card_rects = []
    hovered_index = None
    now = pygame.time.get_ticks()

    for i, char in enumerate(characters):
        center_x = start_x + i * slot_pitch + slot_pitch // 2
        rect = pygame.Rect(center_x - slot_pitch // 2, row_top, slot_pitch, hit_height)
        card_rects.append(rect)
        hovered = rect.collidepoint(mouse_pos)
        if hovered:
            hovered_index = i

        if not dry_run:
            sprite_scale = float(char.get("size", 1.0))
            pulse = 1.0 + (0.055 * math.sin(now / 115)) if hovered else 1.0
            sprite_size = max(32, round(min(scaled(screen, 105) * sprite_scale * pulse, slot_pitch * 0.82)))
            bob = round(math.sin(now / 115) * scaled(screen, 4)) if hovered else 0
            sprite_center_y = row_top + scaled(screen, 62) + bob

            shadow_rect = pygame.Rect(0, 0, round(scaled(screen, 88) * pulse), scaled(screen, 18))
            shadow_rect.center = (center_x, row_top + scaled(screen, 127))
            pygame.draw.ellipse(screen, (29, 32, 46), shadow_rect)
            if hovered:
                glow_rect = shadow_rect.inflate(scaled(screen, 22), scaled(screen, 10))
                pygame.draw.ellipse(screen, (100, 180, 255), glow_rect, width=scaled(screen, 2))

            try:
                sprite_name = char.get("sprite", None)
                if sprite_name:
                    img = get_sprite(sprite_name, (sprite_size, sprite_size))
                    screen.blit(img, img.get_rect(center=(center_x, sprite_center_y)))
            except Exception as e:
                print("SPRITE ERROR:", char["sprite"], e)

            max_name_width = slot_pitch - scaled(screen, 12)
            name_size = name_font_size
            name_font = pygame.font.SysFont(None, name_size)
            while name_font.size(char["name"])[0] > max_name_width and name_size > scaled(screen, 16):
                name_size -= 1
                name_font = pygame.font.SysFont(None, name_size)
            name_color = (255, 239, 171) if hovered else (225, 229, 242)
            name = name_font.render(char["name"], True, name_color)
            screen.blit(name, name.get_rect(midtop=(center_x, row_top + scaled(screen, 139))))

    active_index = confirmation_index
    if active_index is None:
        active_index = hovered_index if hovered_index is not None else selected_index
    if not dry_run:
        if active_index is not None:
            _draw_character_details(screen, characters[active_index], margin)
        else:
            prompt_font = font(screen, 27)
            prompt = prompt_font.render("Hover over a character to inspect their stats and passive", True, (164, 173, 198))
            screen.blit(prompt, prompt.get_rect(center=(width // 2, round(height * 0.72))))

        if confirmation_index is not None:
            _draw_selection_confirmation(screen, characters[confirmation_index], mouse_pos)

    return card_rects


def _draw_character_details(screen, character, margin):
    width, height = screen.get_size()
    panel_width = min(scaled(screen, 760), width - margin * 2)
    panel_height = min(scaled(screen, 300), round(height * 0.47))
    panel = pygame.Rect(0, 0, panel_width, panel_height)
    panel.centerx = width // 2
    panel.bottom = height - scaled(screen, 16)
    pygame.draw.rect(screen, (25, 29, 43), panel, border_radius=scaled(screen, 16))
    pygame.draw.rect(screen, (65, 76, 108), panel, width=scaled(screen, 1), border_radius=scaled(screen, 16))

    inset = scaled(screen, 24)
    name_font = font(screen, 40)
    meta_font = font(screen, 21)
    stat_font = font(screen, 23)
    name = name_font.render(character["name"], True, (255, 244, 204))
    screen.blit(name, (panel.left + inset, panel.top + scaled(screen, 15)))

    passive = character.get("passive") or "No passive"
    if isinstance(passive, list):
        passive = ", ".join(passive)
    passive = str(passive).replace("_", " ").title()
    meta = meta_font.render(f"{character.get('rarity', 'common').title()}  ·  Passive: {passive}", True, (165, 190, 232))
    screen.blit(meta, (panel.left + inset, panel.top + scaled(screen, 53)))

    stats = (
        (f"HP  {character['hp']}", f"HP growth  +{character.get('hp_growth', 0)}"),
        (f"Attack  {character['atk_min']}–{character['atk_max']}", f"Attack growth  +{character.get('atk_growth', 0)}"),
        (f"Speed  {character['attack_speed']:.2f}", f"Crit  {int(character['crit'] * 100)}%"),
        (f"Dodge  {int(character['dodge'] * 100)}%", f"Lifesteal  {int(character['lifesteal'] * 100)}%"),
        (f"Armor  {character['armor']}", f"Magic resist  {character.get('magic_resist', 0)}"),
    )
    column_gap = scaled(screen, 30)
    column_width = (panel.width - inset * 2 - column_gap) // 2
    stats_top = panel.top + scaled(screen, 91)
    row_height = scaled(screen, 27)
    for row, pair in enumerate(stats):
        for column, text in enumerate(pair):
            rendered = stat_font.render(text, True, (225, 230, 242))
            x = panel.left + inset + column * (column_width + column_gap)
            y = stats_top + row * row_height
            screen.blit(rendered, (x, y))

    description_font = font(screen, 22)
    description_y = panel.top + panel.height - scaled(screen, 42)
    draw_text_wrapped(
        screen,
        character.get("description", ""),
        description_font,
        panel.left + inset,
        description_y,
        panel.width - inset * 2,
        color=(184, 194, 215),
    )


def _draw_selection_confirmation(screen, character, mouse_pos):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((5, 7, 14, 175))
    screen.blit(overlay, (0, 0))

    modal, start_button, back_button = selection_confirm_buttons(screen)
    pygame.draw.rect(screen, (32, 38, 57), modal, border_radius=scaled(screen, 18))
    pygame.draw.rect(screen, (112, 139, 194), modal, width=scaled(screen, 2), border_radius=scaled(screen, 18))

    title_font = font(screen, 40)
    body_font = font(screen, 25)
    title = title_font.render(f"Start as {character['name']}?", True, (255, 246, 218))
    screen.blit(title, title.get_rect(center=(modal.centerx, modal.top + scaled(screen, 66))))
    subtitle = body_font.render("Ready to begin this run?", True, (185, 196, 218))
    screen.blit(subtitle, subtitle.get_rect(center=(modal.centerx, modal.top + scaled(screen, 112))))

    for rect, label, color in (
        (start_button, "START GAME", (62, 133, 103)),
        (back_button, "BACK TO SELECTION", (70, 82, 117)),
    ):
        hovered = rect.collidepoint(mouse_pos)
        button_color = tuple(min(255, channel + 20) for channel in color) if hovered else color
        pygame.draw.rect(screen, button_color, rect, border_radius=scaled(screen, 9))
        text = font(screen, 20).render(label, True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=rect.center))

import math
import pygame
from ui.layout import font, menu_buttons, scaled, select_back_button, selection_confirm_buttons, ui_scale

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

def draw_menu(self, screen):
    screen.fill((20, 20, 30))

    font_big = font(screen, 80)
    button_font = font(screen, 40)

    title = font_big.render("TROLL GAME", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(screen.get_width() // 2, round(screen.get_height() * 0.23))))

    labels = (("PLAY", (60, 120, 200)), ("SETTINGS", (80, 80, 80)), ("EXIT GAME", (120, 55, 55)))
    for rect, (label, color) in zip(menu_buttons(screen), labels):
        pygame.draw.rect(screen, color, rect, border_radius=scaled(screen, 10))
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


def draw_game_over(screen):
    screen.fill((15, 15, 25))
    title = font(screen, 88).render("YOU LOSE!", True, (255, 75, 75))
    screen.blit(title, title.get_rect(center=(screen.get_width() // 2, round(screen.get_height() * 0.40))))
    prompt = font(screen, 32).render("Run over. Click anywhere to return to the main menu", True, (205, 210, 225))
    screen.blit(prompt, prompt.get_rect(center=(screen.get_width() // 2, round(screen.get_height() * 0.57))))


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

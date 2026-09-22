import pygame

# -------------------------
# SPRITE CACHE (NO LAG ZONE)
# -------------------------
SPRITE_CACHE = {}

def get_sprite(name):
    if name in SPRITE_CACHE:
        return SPRITE_CACHE[name]

    img = pygame.image.load(f"assets/sprites/{name}").convert_alpha()
    img = pygame.transform.scale(img, (120, 120))
    SPRITE_CACHE[name] = img
    return img

def draw_menu(self, screen):
    screen.fill((20, 20, 30))

    font_big = pygame.font.SysFont(None, 80)
    font = pygame.font.SysFont(None, 40)

    title = font_big.render("TROLL GAME", True, (255, 255, 255))
    screen.blit(title, (250, 100))

    # PLAY BUTTON
    pygame.draw.rect(screen, (60, 120, 200), (350, 220, 200, 60), border_radius=10)
    play = font.render("PLAY", True, (255, 255, 255))
    screen.blit(play, (410, 235))

    # SETTINGS BUTTON
    pygame.draw.rect(screen, (80, 80, 80), (350, 320, 200, 60), border_radius=10)
    settings = font.render("SETTINGS", True, (255, 255, 255))
    screen.blit(settings, (380, 335))

def draw_settings(self, screen):
    screen.fill((15, 15, 25))

    font_big = pygame.font.SysFont(None, 60)
    font = pygame.font.SysFont(None, 30)

    title = font_big.render("SETTINGS", True, (255, 255, 255))
    screen.blit(title, (300, 80))

    info = font.render("Click anywhere to go back", True, (180, 180, 180))
    screen.blit(info, (300, 200))


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
            lines.append(current)
            current = word + " "
        else:
            current = test

    lines.append(current)

    for i, line in enumerate(lines):
        rendered = font.render(line, True, color)
        screen.blit(rendered, (x, y + i * 20))


# -------------------------
# ROUND
# -------------------------
def draw_round(screen, round_number):
    font = pygame.font.SysFont(None, 40)
    text = font.render(f"Round {round_number}", True, (255, 255, 255))
    screen.blit(text, (380, 20))


# -------------------------
# UPGRADES
# -------------------------
def draw_upgrades(screen, upgrades, ready=True):
    font = pygame.font.SysFont(None, 40)

    if not ready:
        text = font.render("Preparing upgrades...", True, (150, 150, 150))
        screen.blit(text, (320, 250))
        return

    for i, upg in enumerate(upgrades):
        pygame.draw.rect(
            screen,
            (40, 40, 60),
            (40, 100 + i * 90, 400, 70),
            border_radius=8
        )
        text = font.render(f"{i+1}: {upg['name']}", True, (255, 255, 255))
        screen.blit(text, (60, 120 + i * 90))


# -------------------------
# STATS PANEL (BATTLE)
# -------------------------
def draw_stats(screen, character, x, y):
    font = pygame.font.SysFont(None, 26)
    title_font = pygame.font.SysFont(None, 32)

    panel_width = 220
    panel_height = 190

    pygame.draw.rect(
        screen,
        (30, 30, 45),
        (x - 10, y - 10, panel_width, panel_height),
        border_radius=10
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
        text = font.render(line, True, (220, 220, 220))
        screen.blit(text, (x, y + 35 + i * 18))


# -------------------------
# RESULT
# -------------------------
def draw_result(screen, result):
    font_big = pygame.font.SysFont(None, 100)
    font_small = pygame.font.SysFont(None, 40)

    if result == "player":
        text = font_big.render("YOU WIN!", True, (255, 220, 80))
    else:
        text = font_big.render("YOU LOSE!", True, (255, 60, 60))

    screen.blit(text, (260, 200))

    sub = font_small.render("Preparing upgrades...", True, (180, 180, 180))
    screen.blit(sub, (300, 320))


# -------------------------
# CHARACTER SELECT (CLEAN + “CSS FEEL”)
# -------------------------
def draw_character_select(screen, characters, selected_index, mouse_pos, dry_run=False):

    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 40)

    start_x = 60
    spacing = 150

    card_rects = []

    for i, char in enumerate(characters):

        x = start_x + i * spacing
        y = 90

        rect = pygame.Rect(x, y, 90, 120)
        card_rects.append(rect)

        hovered = rect.collidepoint(mouse_pos)

        # COLORS (simple “UI feel”)
        if selected_index == i:
            color = (220, 200, 80)
        elif hovered:
            color = (120, 120, 180)
        else:
            color = (45, 45, 65)

        if not dry_run:

            # CARD BACKGROUND
            pygame.draw.rect(screen, color, rect, border_radius=10)

            # HOVER GLOW EFFECT
            if hovered:
                pygame.draw.rect(screen, (180, 180, 255), rect, 2, border_radius=10)

            # SPRITE
            try:
                sprite_name = char.get("sprite", None)
                if sprite_name:
                    img = get_sprite(sprite_name)
                    screen.blit(img, (x + 15, y + 10))
                screen.blit(img, (x + 15, y + 10))
            except Exception as e:
                print("SPRITE ERROR:", char["sprite"], e)

            # NAME
            name = font.render(char["name"], True, (255, 255, 255))
            screen.blit(name, (x, y + 80))

            # INDEX
            key = font.render(f"{i+1}", True, (180, 180, 180))
            screen.blit(key, (x + 35, y - 20))

    # -------------------------
    # DETAILS PANEL (RIGHT SIDE)
    # -------------------------
    if not dry_run and selected_index is not None:

        char = characters[selected_index]

        panel_x = 320
        panel_y = 250

        pygame.draw.rect(
            screen,
            (25, 25, 35),
            (panel_x - 10, panel_y - 10, 360, 300),
            border_radius=12
        )

        title = big_font.render(char["name"], True, (255, 255, 255))
        screen.blit(title, (panel_x, panel_y))

        stats = [
            f"HP: {char['hp']}",
            f"ATK: {char['atk_min']}-{char['atk_max']}",
            f"SPD: {char['attack_speed']}",
            f"CRIT: {int(char['crit'] * 100)}%",
            f"DODGE: {int(char['dodge'] * 100)}%",
            f"LS: {int(char['lifesteal'] * 100)}%",
            f"ARMOR: {char['armor']}",
        ]

        for i, line in enumerate(stats):
            txt = font.render(line, True, (220, 220, 220))
            screen.blit(txt, (panel_x, panel_y + 40 + i * 22))

        draw_text_wrapped(
            screen,
            char["description"],
            font,
            panel_x,
            panel_y + 200,
            320
        )

        confirm = big_font.render("CLICK TO START", True, (255, 255, 255))
        screen.blit(confirm, (panel_x, panel_y + 270))

    return card_rects
import pygame

# -------------------------
# SPRITE CACHE (FIXES LAG)
# -------------------------

SPRITE_CACHE = {}

def get_sprite(name):
    if name in SPRITE_CACHE:
        return SPRITE_CACHE[name]

    img = pygame.image.load(f"assets/sprites/{name}").convert_alpha()
    img = pygame.transform.scale(img, (60, 60))
    SPRITE_CACHE[name] = img
    return img


# -------------------------
# UI DRAW FUNCTIONS
# -------------------------

def draw_round(screen, round_number):
    font = pygame.font.SysFont(None, 40)
    text = font.render(f"Round {round_number}", True, (255, 255, 255))
    screen.blit(text, (380, 20))


def draw_upgrades(screen, upgrades, ready=True):
    font = pygame.font.SysFont(None, 40)

    if not ready:
        text = font.render("Preparing upgrades...", True, (150, 150, 150))
        screen.blit(text, (320, 250))
        return

    for i, upg in enumerate(upgrades):
        pygame.draw.rect(screen, (40, 40, 60), (40, 100 + i * 90, 400, 70), border_radius=8)

        text = font.render(f"{i+1}: {upg[0]}", True, (255, 255, 255))
        screen.blit(text, (60, 120 + i * 90))


def draw_stats(screen, character, x, y):
    font = pygame.font.SysFont(None, 28)

    stats = [
        f"HP: {int(character.hp)}/{int(character.max_hp)}",
        f"ATK: {character.atk_min}-{character.atk_max}",
        f"CRIT: {int(character.crit * 100)}%",
        f"DODGE: {int(character.dodge * 100)}%",
        f"LS: {int(character.lifesteal * 100)}%",
    ]

    for i, line in enumerate(stats):
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (x, y + i * 20))


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


def draw_character_select(screen, characters, selected_index, mouse_pos, dry_run=False):
    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 40)

    start_x = 50
    spacing = 160

    card_rects = []

    for i, char in enumerate(characters):
        x = start_x + i * spacing
        y = 80   # 🔼 moved UP

        rect = pygame.Rect(x, y, 80, 110)
        card_rects.append(rect)

        hovered = rect.collidepoint(mouse_pos)

        if selected_index == i:
            color = (200, 200, 80)
        elif hovered:
            color = (120, 120, 180)
        else:
            color = (40, 40, 60)

        if not dry_run:
            pygame.draw.rect(screen, color, rect, border_radius=8)

            # ✅ FIXED SPRITE LOADING (no .png duplication)
            try:
                img = get_sprite(char["sprite"])  # <-- IMPORTANT
                screen.blit(img, (x + 10, y + 10))
            except Exception as e:
                print("SPRITE ERROR:", char["sprite"], e)

            name = font.render(char["name"], True, (255, 255, 255))
            screen.blit(name, (x, y + 90))

            key = font.render(f"{i+1}", True, (180, 180, 180))
            screen.blit(key, (x + 30, y - 20))

    # -------------------------
    # DETAILS PANEL (moved DOWN)
    # -------------------------

    if not dry_run and selected_index is not None:
        char = characters[selected_index]

        base_y = 250  # 🔽 moved DOWN

        title = big_font.render(char["name"], True, (255, 255, 255))
        screen.blit(title, (300, base_y))

        stats = [
            f"HP: {char['hp']}",
            f"ATK: {char['atk_min']}-{char['atk_max']}",
            f"AS: {char['attack_speed']}",
            f"CRIT: {int(char['crit'] * 100)}%",
            f"DODGE: {int(char['dodge'] * 100)}%",
        ]

        for i, line in enumerate(stats):
            txt = font.render(line, True, (220, 220, 220))
            screen.blit(txt, (300, base_y + 40 + i * 25))

        desc = font.render(char["description"], True, (180, 180, 180))
        screen.blit(desc, (300, base_y + 180))

        confirm = big_font.render("CLICK to start", True, (255, 255, 255))
        screen.blit(confirm, (300, base_y + 230))

    return card_rects

    # -------------------------
    # DETAILS PANEL
    # -------------------------

    if not dry_run and selected_index is not None:
        char = characters[selected_index]

        title = big_font.render(char["name"], True, (255, 255, 255))
        screen.blit(title, (300, 100))

        stats = [
            f"HP: {char['hp']}",
            f"ATK: {char['atk_min']}-{char['atk_max']}",
            f"AS: {char['attack_speed']}",
            f"CRIT: {int(char['crit'] * 100)}%",
            f"DODGE: {int(char['dodge'] * 100)}%",
        ]

        for i, line in enumerate(stats):
            txt = font.render(line, True, (220, 220, 220))
            screen.blit(txt, (300, 140 + i * 25))

        desc = font.render(char["description"], True, (180, 180, 180))
        screen.blit(desc, (300, 300))

        confirm = big_font.render("CLICK to start", True, (255, 255, 255))
        screen.blit(confirm, (300, 350))

    return card_rects
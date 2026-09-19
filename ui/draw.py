import pygame


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
        color = (255, 255, 255)

        # make them feel "selectable cards"
        pygame.draw.rect(screen, (40, 40, 60), (40, 100 + i * 90, 400, 70), border_radius=8)

        text = font.render(f"{i+1}: {upg[0]}", True, color)
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

def draw_character_select(screen, characters, selected_index):
    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 40)

    start_x = 50
    spacing = 160

    for i, char in enumerate(characters):
        x = start_x + i * spacing
        y = 200

        # highlight selected
        if selected_index == i:
            pygame.draw.rect(screen, (200, 200, 80), (x-5, y-5, 90, 120), border_radius=8)

        # card background
        pygame.draw.rect(screen, (40, 40, 60), (x, y, 80, 110), border_radius=8)

        # name
        name = font.render(char["name"], True, (255, 255, 255))
        screen.blit(name, (x, y + 90))

        # key hint
        key = font.render(f"{i+1}", True, (180, 180, 180))
        screen.blit(key, (x + 30, y - 20))

    # selected details
    if selected_index is not None:
        char = characters[selected_index]

        title = big_font.render(char["name"], True, (255, 255, 255))
        screen.blit(title, (300, 100))

        stats = [
            f"HP: {char['hp']}",
            f"ATK: {char['atk_min']}-{char['atk_max']}",
            f"AS: {char['attack_speed']}",
            f"CRIT: {int(char['crit']*100)}%",
            f"DODGE: {int(char['dodge']*100)}%",
        ]

        for i, line in enumerate(stats):
            txt = font.render(line, True, (220, 220, 220))
            screen.blit(txt, (300, 140 + i * 25))

        desc = font.render(char["description"], True, (180, 180, 180))
        screen.blit(desc, (300, 300))

        confirm = big_font.render("ENTER to start", True, (255, 255, 255))
        screen.blit(confirm, (300, 350))
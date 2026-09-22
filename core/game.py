import pygame

from core.entities import Character
from core.battle import Battle
from core.enemy_factory import generate_enemy
from core.upgrades import get_random_upgrades
from core.character_factory import get_random_characters

from ui.draw import (
    draw_round,
    draw_upgrades,
    draw_stats,
    draw_result,
    draw_character_select,
)


class Game:

    def __init__(self):
        self.round = 1

        # -------------------------
        # BUTTONS
        # -------------------------
        from ui.button import Button

        self.font_btn = pygame.font.SysFont(None, 40)

        self.upgrade_buttons = []

        self.play_button = Button(
            (350, 220, 200, 60),
            "PLAY",
            self.font_btn,
            (60, 160, 60),
            (100, 200, 100),
        )

        self.settings_button = Button(
            (350, 320, 200, 60),
            "SETTINGS",
            self.font_btn,
            (60, 60, 160),
            (100, 100, 200),
        )

        self.back_button = Button(
            (350, 400, 200, 60),
            "BACK",
            self.font_btn,
            (160, 60, 60),
            (200, 80, 80),
        )

        # -------------------------
        # STATE
        # -------------------------
        self.state = "menu"

        # -------------------------
        # SELECT
        # -------------------------
        self.character_choices = get_random_characters(5)
        self.selected_index = None
        self.card_rects = []

        # -------------------------
        # GAME OBJECTS
        # -------------------------
        self.player = None
        self.enemy = None
        self.battle = None

        # -------------------------
        # UPGRADES / RESULT
        # -------------------------
        self.upgrades = []
        self.upgrade_timer = 0
        self.upgrade_ready = False

        self.result = None
        self.result_timer = 0

    # -------------------------
    # START GAME
    # -------------------------
    def start_game_with_character(self, index):
        data = self.character_choices[index]

        self.player = Character(
            150, 250,
            data["hp"],
            data["atk_min"],
            data["atk_max"],
            (50, 150, 255),
            crit=data.get("crit", 0),
            dodge=data.get("dodge", 0),
            lifesteal=data.get("lifesteal", 0),
            attack_speed=data.get("attack_speed", 1.0),
            armor=data.get("armor", 0),
            magic_resist=data.get("magic_resist", 0),
            magic_damage=data.get("magic_damage", 0.0),
            hp_growth=data.get("hp_growth", 0),
            atk_growth=data.get("atk_growth", 0),
            size=data.get("size", 1.0),
            on_hit=data.get("on_hit", []),
            main_stat=data.get("main_stat"),
            rarity=data.get("rarity", "common"),
            name=data["name"],
            sprite_name=data.get("sprite"),
        )

        self.enemy = generate_enemy(self.round)
        self.battle = Battle(self.player, self.enemy)

        self.state = "battle"

    # -------------------------
    # UPGRADE INIT (SAFE RESET)
    # -------------------------
    def start_upgrade(self):
        self.upgrades = get_random_upgrades(3)

        from ui.button import Button
        font_btn = pygame.font.SysFont(None, 30)

        self.upgrade_buttons = []

        start_x = 200
        y = 250
        spacing = 220

        for i, upg in enumerate(self.upgrades):
            rect = (start_x + i * spacing, y, 200, 80)
            self.upgrade_buttons.append(
                Button(rect, upg[0], font_btn, (80, 80, 120), (120, 120, 180))
            )

        self.upgrade_ready = False
        self.upgrade_timer = pygame.time.get_ticks()

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, keys, mouse_pos, mouse_click):

        # MENU
        if self.state == "menu":
            self.play_button.update(mouse_pos)
            self.settings_button.update(mouse_pos)

            if self.play_button.is_clicked(mouse_pos, mouse_click):
                self.state = "select"

            if self.settings_button.is_clicked(mouse_pos, mouse_click):
                self.state = "settings"

            return

        # SELECT
        if self.state == "select":
            self.card_rects = draw_character_select(
                None,
                self.character_choices,
                self.selected_index,
                mouse_pos,
                dry_run=True
            )

            self.selected_index = None

            for i, rect in enumerate(self.card_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    if mouse_click:
                        self.start_game_with_character(i)
                        return
            return

        # BATTLE
        if self.state == "battle":
            if not self.battle.finished:
                self.battle.update()
            else:
                self.result = self.battle.winner
                self.result_timer = pygame.time.get_ticks()
                self.state = "result"
            return

        # RESULT
        if self.state == "result":
            if pygame.time.get_ticks() - self.result_timer > 1200:
                self.state = "upgrade"
                self.start_upgrade()
            return

        # UPGRADE (FIXED CLEAN FLOW)
        if self.state == "upgrade":

            if not self.upgrade_ready:
                if pygame.time.get_ticks() - self.upgrade_timer > 400:
                    self.upgrade_ready = True

            if not self.upgrade_ready:
                return

            for i, btn in enumerate(self.upgrade_buttons):
                btn.update(mouse_pos)

                if btn.is_clicked(mouse_pos, mouse_click):
                    self.player.apply_upgrade(self.upgrades[i])
                    self.state = "next"
                    return

            return

        # NEXT ROUND
        if self.state == "next":
            self.round += 1
            self.player.hp = self.player.max_hp
            self.enemy = generate_enemy(self.round)
            self.battle = Battle(self.player, self.enemy)
            self.state = "battle"
            return

        # SETTINGS
        if self.state == "settings":
            self.back_button.update(mouse_pos)

            if keys[pygame.K_ESCAPE]:
                self.state = "menu"

            if self.back_button.is_clicked(mouse_pos, mouse_click):
                self.state = "menu"

    # -------------------------
    # DRAW
    # -------------------------
    def draw(self, screen):

        screen.fill((20, 20, 30))
        draw_round(screen, self.round)

        if self.state == "menu":
            self.draw_menu(screen)
            return

        elif self.state == "settings":
            self.draw_settings(screen)
            return

        elif self.state == "battle":
            self.battle.draw(screen)
            draw_stats(screen, self.player, 20, 400)
            draw_stats(screen, self.enemy, 700, 400)

        elif self.state == "result":
            self.battle.draw(screen)
            draw_result(screen, self.result)

        elif self.state == "upgrade":
            for btn in self.upgrade_buttons:
                btn.draw(screen)
            draw_stats(screen, self.player, 20, 400)

        elif self.state == "select":
            self.card_rects = draw_character_select(
                screen,
                self.character_choices,
                self.selected_index,
                pygame.mouse.get_pos()
            )

    # -------------------------
    # MENU
    # -------------------------
    def draw_menu(self, screen):
        font_big = pygame.font.SysFont(None, 80)

        title = font_big.render("Rune's Game", True, (255, 255, 255))
        screen.blit(title, (260, 100))

        self.play_button.draw(screen)
        self.settings_button.draw(screen)

    # -------------------------
    # SETTINGS
    # -------------------------
    def draw_settings(self, screen):
        font_big = pygame.font.SysFont(None, 60)
        font = pygame.font.SysFont(None, 30)

        title = font_big.render("SETTINGS", True, (255, 255, 255))
        screen.blit(title, (300, 80))

        lines = [
            "Resolution: 900x600 (for now)",
            "Volume: not implemented yet",
        ]

        for i, line in enumerate(lines):
            txt = font.render(line, True, (200, 200, 200))
            screen.blit(txt, (260, 200 + i * 40))

        self.back_button.draw(screen)
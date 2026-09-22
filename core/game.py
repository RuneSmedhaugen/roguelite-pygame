import pygame

from core.entities import Character
from core.battle import Battle
from core.enemy_factory import generate_enemy
from core.upgrades import get_random_upgrades
from core.character_factory import build_character
from core.character_factory import get_random_characters

from ui.draw import (
    draw_menu,
    draw_character_select,
    draw_upgrades,
    draw_round,
    draw_stats,
    draw_result,
)


class Game:
    def __init__(self):
        self.round = 1
        self.state = "menu"

        # data
        self.character_choices = []
        self.selected_index = None
        self.player = None
        self.enemy = None
        self.battle = None
        self.result = None
        self.click_lock = False

        # upgrades
        self.upgrades = []

        # init choices immediately (so select screen works)
        self.character_choices = get_random_characters(5)

    # -------------------------
    # START GAME
    # -------------------------
    def start_game_with_character(self, index):
        raw = self.character_choices[index]

        self.player = build_character(raw, x=150, y=250)
        self.player.color = (50, 150, 255)

        self.enemy = generate_enemy(self.round)
        self.battle = Battle(self.player, self.enemy)

        self.state = "battle"

    # -------------------------
    # UPGRADES
    # -------------------------
    def start_upgrade(self):
        self.upgrades = get_random_upgrades(3)

    # -------------------------
    # UPDATE LOOP (LOGIC ONLY)
    # -------------------------
    def update(self, keys, mouse_pos, mouse_click):
        if not mouse_click:
            self.click_lock = False

        # MENU
        if self.state == "menu":
            if mouse_click:
                self.state = "select"
            return

        # SELECT
        if self.state == "select":
            # simple click-to-select version
            rects = draw_character_select(
                None,
                self.character_choices,
                self.selected_index,
                mouse_pos,
                dry_run=True
            )

            if mouse_click and rects:
                for i, r in enumerate(rects):
                    if r.collidepoint(mouse_pos):
                        self.start_game_with_character(i)
                        return
            return

        # BATTLE
        if self.state == "battle":
            if not self.battle.finished:
                self.battle.update()
            else:
                self.result = self.battle.winner
                self.state = "result"
            return

        # RESULT
        if self.state == "result":
            if mouse_click and not self.click_lock:
                self.click_lock = True
                self.state = "upgrade"
                self.start_upgrade()
            return

        # UPGRADE
        if self.state == "upgrade":
            if mouse_click and not self.click_lock:
                self.click_lock = True
                chosen = 0
                self.player.apply_upgrade(self.upgrades[chosen])
                self.state = "next"
            return

        # NEXT ROUND
        if self.state == "next":
            self.round += 1
            self.player.hp = self.player.max_hp
            self.enemy = generate_enemy(self.round)
            self.battle = Battle(self.player, self.enemy)
            self.state = "battle"
            return

    # -------------------------
    # DRAW LOOP (RENDER ONLY)
    # -------------------------
    def draw(self, screen, mouse_pos):

        if self.state == "menu":
            draw_menu(self, screen)

        elif self.state == "select":
            draw_character_select(
                screen,
                self.character_choices,
                self.selected_index,
                mouse_pos
            )

        elif self.state == "battle":
            screen.fill((20, 20, 30))
            draw_round(screen, self.round)

            if self.player:
                draw_stats(screen, self.player, 40, 80)

            if self.enemy:
                draw_stats(screen, self.enemy, 600, 80)

        elif self.state == "result":
            screen.fill((10, 10, 15))
            draw_result(screen, self.result)

        elif self.state == "upgrade":
            screen.fill((15, 15, 20))
            draw_upgrades(screen, self.upgrades)

        pygame.display.flip()
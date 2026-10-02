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
        from ui.ui_renderer import UIRenderer
        self.ui = UIRenderer()

        self.round = 1
        self.state = "menu"

        # data
        self.lives = 5
        self.character_choices = []
        self.selected_index = None
        self.player = None
        self.enemy = None
        self.battle = None
        self.result = None
        self.click_lock = False
        self.selected_upgrade = None

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
        self.upgrade_rects = []

    def reset_run(self):
        self.round = 1
        self.lives = 5
        self.player = None
        self.enemy = None
        self.battle = None
        self.result = None
        self.state = "menu"

    
    # -------------------------
    # UPDATE LOOP (LOGIC ONLY)
    # -------------------------
    def update(self, keys, mouse_pos, mouse_click):
        if not mouse_click:
            self.click_lock = False

        # MENU
        if self.state == "menu":
            if mouse_click and not self.click_lock:
                self.click_lock = True

                play_button = pygame.Rect(350, 220, 200, 60)

                if play_button.collidepoint(mouse_pos):
                    print("CLICK PLAY")
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

                if self.result == "enemy":
                    self.lives -= 1
                    print (f"LIFE LOST! Lives remaining: {self.lives}")

                self.state = "result"
            return

        # RESULT
        if self.state == "result":
            if self.lives <= 0:
                self.state = "game_over"
                return

            if mouse_click and not self.click_lock:
                self.click_lock = True
                self.state = "upgrade"
                self.start_upgrade()
            return

        # UPGRADE
        if self.state == "upgrade":

            if mouse_click and not self.click_lock:
                self.click_lock = True

                for i, r in enumerate(self.upgrade_rects):
                    if r.collidepoint(mouse_pos):

                        upg = self.upgrades[i]

                        # -------- BEFORE SNAPSHOT --------
                        before = {
                            "hp": self.player.hp,
                            "max_hp": self.player.max_hp,
                            "atk_min": self.player.atk_min,
                            "atk_max": self.player.atk_max,
                            "crit": self.player.crit,
                            "dodge": self.player.dodge,
                            "lifesteal": self.player.lifesteal,
                            "attack_speed": self.player.attack_speed,
                            "armor": self.player.armor,
                        }

                        print("\n===== UPGRADE START =====")
                        print("SELECTED:", upg)
                        print("BEFORE:", before)

                        # APPLY
                        self.player.apply_upgrade(upg)

                        # -------- AFTER SNAPSHOT --------
                        after = {
                            "hp": self.player.hp,
                            "max_hp": self.player.max_hp,
                            "atk_min": self.player.atk_min,
                            "atk_max": self.player.atk_max,
                            "crit": self.player.crit,
                            "dodge": self.player.dodge,
                            "lifesteal": self.player.lifesteal,
                            "attack_speed": self.player.attack_speed,
                            "armor": self.player.armor,
                        }

                        print("AFTER: ", after)

                        # -------- DIFF HIGHLIGHT --------
                        print("CHANGES:")
                        for k in before:
                            if before[k] != after[k]:
                                print(f"  {k}: {before[k]} -> {after[k]}")

                        print("===== UPGRADE END =====\n")

                        self.state = "next"
                        break

            return

        # NEXT ROUND
        if self.state == "next":
            self.round += 1
            self.player.hp = self.player.max_hp
            self.enemy = generate_enemy(self.round)
            self.battle = Battle(self.player, self.enemy)
            self.state = "battle"
            return

        if self.state == "game_over":
            if mouse_click and not self.click_lock:
                self.click_lock = True
                self.reset_run()
            return

    # -------------------------
    # DRAW LOOP (RENDER ONLY)
    # -------------------------
    def draw(self, screen, mouse_pos):
        self.ui.draw(self, screen, mouse_pos)
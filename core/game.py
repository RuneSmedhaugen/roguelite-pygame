import pygame

from core.entities import Character
from core.battle import Battle
from core.enemy_factory import generate_enemy
from core.upgrades import get_random_upgrades

from ui.draw import (
    draw_round,
    draw_upgrades,
    draw_stats,
    draw_result,
    draw_character_select
)

from core.character_factory import get_random_characters


class Game:

    def __init__(self):
        self.round = 1

        # STATE
        self.state = "select"

        # CHARACTER SELECT
        self.character_choices = get_random_characters(5)
        self.selected_index = None
        self.card_rects = []

        # GAME OBJECTS
        self.player = None
        self.enemy = None
        self.battle = None

        # UPGRADES / RESULT
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
    # UPDATE LOOP
    # -------------------------

    def update(self, keys, mouse_pos, mouse_click):

        # -------------------------
        # SELECT STATE
        # -------------------------
        if self.state == "select":

            # update card rects (no drawing here)
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

        # -------------------------
        # BATTLE STATE
        # -------------------------
        elif self.state == "battle":

            if not self.battle.finished:
                self.battle.update()
            else:
                self.result = self.battle.winner
                self.result_timer = pygame.time.get_ticks()
                self.state = "result"

        # -------------------------
        # RESULT STATE
        # -------------------------
        elif self.state == "result":

            if pygame.time.get_ticks() - self.result_timer > 1200:
                self.state = "upgrade"

                self.upgrades = get_random_upgrades(3)
                self.upgrade_ready = False
                self.upgrade_timer = pygame.time.get_ticks()

        # -------------------------
        # UPGRADE STATE
        # -------------------------
        elif self.state == "upgrade":

            if not self.upgrade_ready:
                if pygame.time.get_ticks() - self.upgrade_timer > 400:
                    self.upgrade_ready = True

            if not self.upgrade_ready:
                return

            if keys[pygame.K_1]:
                self.player.apply_upgrade(self.upgrades[0])
                self.state = "next"

            if keys[pygame.K_2]:
                self.player.apply_upgrade(self.upgrades[1])
                self.state = "next"

            if keys[pygame.K_3]:
                self.player.apply_upgrade(self.upgrades[2])
                self.state = "next"

        # -------------------------
        # NEXT ROUND
        # -------------------------
        elif self.state == "next":

            self.round += 1
            self.player.hp = self.player.max_hp

            self.enemy = generate_enemy(self.round)
            self.battle = Battle(self.player, self.enemy)

            self.state = "battle"

    # -------------------------
    # DRAW LOOP
    # -------------------------

    def draw(self, screen):

        screen.fill((20, 20, 30))

        draw_round(screen, self.round)

        if self.state == "battle":
            self.battle.draw(screen)
            draw_stats(screen, self.player, 20, 400)
            draw_stats(screen, self.enemy, 700, 400)

        elif self.state == "result":
            self.battle.draw(screen)
            draw_result(screen, self.result)

        elif self.state == "upgrade":
            draw_upgrades(screen, self.upgrades, self.upgrade_ready)
            draw_stats(screen, self.player, 20, 400)

        elif self.state == "select":
            self.card_rects = draw_character_select(
                screen,
                self.character_choices,
                self.selected_index,
                pygame.mouse.get_pos()
            )
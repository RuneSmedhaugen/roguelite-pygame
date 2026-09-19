import pygame

from core.entities import Character
from core.battle import Battle
from core.enemy_factory import generate_enemy
from core.upgrades import get_random_upgrades
from ui.draw import draw_round, draw_upgrades, draw_stats, draw_result
from ui.draw import draw_character_select


class Game:

    def __init__(self):
        from core.character_factory import get_random_characters

        self.round = 1

        self.state = "select"
        self.character_choices = get_random_characters(5)
        self.selected_index = None

        self.player = Character(150, 250, 120, 4, 8, (50, 150, 255))
        self.enemy = generate_enemy(self.round)

        self.battle = Battle(self.player, self.enemy)

        # timing / state control
        self.upgrade_timer = 0
        self.upgrade_ready = False

        self.result = None
        self.result_timer = 0

        self.state = "select"
        self.upgrades = []

    def update(self, keys):

        # -------------------------
        # BATTLE STATE
        # -------------------------
        if self.state == "battle":

            if not self.battle.finished:
                self.battle.update()

            else:
                # ENTER RESULT STATE (ONLY DISPLAY INFO HERE)
                self.result = self.battle.winner
                self.result_timer = pygame.time.get_ticks()

                self.state = "result"

        # -------------------------
        # RESULT STATE (dramatic pause)
        # -------------------------
        elif self.state == "result":

            if pygame.time.get_ticks() - self.result_timer > 1200:

                # transition to upgrade screen
                self.state = "upgrade"

                # ONLY NOW generate upgrades
                self.upgrades = get_random_upgrades(3)

                self.upgrade_ready = False
                self.upgrade_timer = pygame.time.get_ticks()

        # -------------------------
        # UPGRADE STATE
        # -------------------------
        elif self.state == "upgrade":

            # small delay before input allowed
            if not self.upgrade_ready:
                now = pygame.time.get_ticks()
                if now - self.upgrade_timer > 400:
                    self.upgrade_ready = True

            if not self.upgrade_ready:
                return

            # selection
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
        # NEXT ROUND SETUP
        # -------------------------
        elif self.state == "next":

            self.round += 1

            self.player.hp = self.player.max_hp
            self.enemy = generate_enemy(self.round)
            self.battle = Battle(self.player, self.enemy)

            self.state = "battle"

        elif self.state == "select":

            # number keys to select
            if keys[pygame.K_1]:
                self.selected_index = 0
            if keys[pygame.K_2]:
                self.selected_index = 1
            if keys[pygame.K_3]:
                self.selected_index = 2
            if keys[pygame.K_4]:
                self.selected_index = 3
            if keys[pygame.K_5]:
                self.selected_index = 4

            # confirm selection (ENTER)
            if keys[pygame.K_RETURN] and self.selected_index is not None:
                data = self.character_choices[self.selected_index]

                # create actual Character object
                self.player = Character(
                    150, 250,
                    data["hp"],
                    data["atk_min"],
                    data["atk_max"],
                    (50, 150, 255),
                    crit=data["crit"],
                    dodge=data["dodge"],
                    lifesteal=data["lifesteal"],
                    sprite_name=data["sprite"]
                )

                self.enemy = generate_enemy(self.round)
                self.battle = Battle(self.player, self.enemy)

                self.state = "battle"

    def draw(self, screen):

        screen.fill((20, 20, 30))

        # always visible
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

        elif self.state == "next":
            pass

        elif self.state == "select":
            draw_character_select(screen, self.character_choices, self.selected_index)
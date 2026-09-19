import random

import pygame
import os

class Character:
    # -------------------------
    # CORE SETUP
    # -------------------------
    def __init__(self, x, y, hp, atk_min, atk_max, color,
                 crit=0.1, dodge=0.05, lifesteal=0.0, sprite_name=None):

        self.x = x
        self.y = y

        self.hp = hp
        self.max_hp = hp

        self.atk_min = atk_min
        self.atk_max = atk_max

        self.crit = crit
        self.dodge = dodge
        self.lifesteal = lifesteal

        self.color = color
        self.sprite = None
        if sprite_name:
            path = os.path.join("assets", "sprites", sprite_name)
            self.sprite = pygame.image.load(path).convert_alpha()
            self.sprite = pygame.transform.scale(self.sprite, (80, 80))

    # -------------------------
    # COMBAT SYSTEM
    # -------------------------
    def attack(self, other):
        damage = random.randint(self.atk_min, self.atk_max)

        # crit
        if random.random() < self.crit:
            damage *= 2

        # dodge
        if random.random() < other.dodge:
            damage = 0

        other.hp -= damage

        # lifesteal
        heal = damage * self.lifesteal
        self.hp = min(self.max_hp, self.hp + heal)


    def is_alive(self):
        return self.hp > 0

    # -------------------------
    # PROGRESSION SYSTEM
    # -------------------------
    def apply_upgrade(self, upgrade):
        name, stat, value = upgrade

        if stat == "hp":
            self.max_hp += value
            self.hp += value

        elif stat == "atk":
            if isinstance(value, tuple):
                import random
                bonus = random.randint(value[0], value[1])
            else:
                bonus = value

            self.atk_min += bonus
            self.atk_max += bonus

        elif stat == "crit":
            self.crit += value

        elif stat == "dodge":
            self.dodge += value

        elif stat == "lifesteal":
            self.lifesteal += value
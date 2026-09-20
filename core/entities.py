import random

import pygame
import os

class Character:
    def __init__(
        self,
        x,
        y,
        hp,
        atk_min,
        atk_max,
        color,
        crit=0.1,
        dodge=0.05,
        lifesteal=0.0,
        attack_speed=1.0,
        armor=0,
        magic_resist=0,
        magic_damage=0.0,
        hp_growth=0,
        atk_growth=0,
        size=1.0,
        on_hit=None,
        main_stat=None,
        rarity="common",
        sprite_name=None,
    ):
        self.x = x
        self.y = y

        self.hp = hp
        self.max_hp = hp

        self.atk_min = atk_min
        self.atk_max = atk_max

        self.crit = crit
        self.dodge = dodge
        self.lifesteal = lifesteal

        self.attack_speed = attack_speed

        self.armor = armor
        self.magic_resist = magic_resist
        self.magic_damage = magic_damage

        self.hp_growth = hp_growth
        self.atk_growth = atk_growth

        self.size = size
        self.on_hit = on_hit or []

        self.main_stat = main_stat
        self.rarity = rarity

        self.sprite_name = sprite_name
        self.color = color
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
"""Single-player upgrade offers and weighted selection."""

import random


UPGRADES = [
    {"name": "+HP", "stat": "hp", "value": 20, "weight": 10},
    {"name": "+DAMAGE", "stat": "atk", "value": (1, 2), "weight": 10},
    {"name": "+CRIT", "stat": "crit", "value": 0.05, "weight": 7},
    {"name": "+DODGE", "stat": "dodge", "value": 0.03, "weight": 7},
    {"name": "+LIFESTEAL", "stat": "lifesteal", "value": 0.05, "weight": 5},
    {"name": "+ATTACK SPEED", "stat": "attack_speed", "value": 0.1, "weight": 9},
]


def get_random_upgrades(count=3):
    choices = UPGRADES[:]
    selected = []

    for _ in range(min(count, len(choices))):
        total = sum(upgrade["weight"] for upgrade in choices)
        pick = random.uniform(0, total)
        upto = 0
        for upgrade in choices:
            upto += upgrade["weight"]
            if upto >= pick:
                selected.append(upgrade)
                choices.remove(upgrade)
                break

    return selected

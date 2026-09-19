import random


UPGRADES = [
    ("+HP", "hp", 20),
    ("+DAMAGE", "atk", (1, 2)),
    ("+CRIT", "crit", 0.05),
    ("+DODGE", "dodge", 0.03),
    ("+LIFESTEAL", "lifesteal", 0.05),
]


def get_random_upgrades(n=3):
    return random.sample(UPGRADES, n)
import random
from core.entities import Character


def generate_enemy(round_number):
    # base scaling
    base_hp = 90 + round_number * 10
    base_min = 3 + round_number * 0.5
    base_max = 6 + round_number * 0.7

    # randomness
    hp = int(base_hp * random.uniform(0.9, 1.2))
    atk_min = int(base_min * random.uniform(0.8, 1.2))
    atk_max = int(base_max * random.uniform(0.8, 1.3))

    # random traits
    crit = random.choice([0.05, 0.1, 0.15])
    dodge = random.choice([0.02, 0.05, 0.1])
    lifesteal = random.choice([0.0, 0.03, 0.05])

    return Character(
        650, 250,
        hp,
        atk_min,
        atk_max,
        (255, 80, 80),
        crit=crit,
        dodge=dodge,
        lifesteal=lifesteal
    )
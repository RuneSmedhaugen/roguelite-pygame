import random

UPGRADES = [
    {"name": "+HP", "stat": "hp", "value": 20, "weight": 10},

    # FIX: applies to BOTH atk_min and atk_max safely
    {"name": "+DAMAGE", "stat": "atk", "value": (1, 2), "weight": 10},

    {"name": "+CRIT", "stat": "crit", "value": 0.05, "weight": 7},
    {"name": "+DODGE", "stat": "dodge", "value": 0.03, "weight": 7},
    {"name": "+LIFESTEAL", "stat": "lifesteal", "value": 0.05, "weight": 5},
    {"name": "+ATTACK SPEED", "stat": "attack_speed", "value": 0.1, "weight": 9},
]


def apply_upgrade(character, upgrade):
    """
    Central upgrade handler (important missing piece).
    Keeps logic consistent everywhere.
    """

    stat = upgrade["stat"]
    value = upgrade["value"]

    # HP upgrade
    if stat == "hp":
        character.max_hp += value
        character.hp += value
        return

    # DAMAGE upgrade (min/max split)
    if stat == "atk":
        min_inc, max_inc = value
        character.atk_min += min_inc
        character.atk_max += max_inc
        return

    # flat stat upgrades
    if hasattr(character, stat):
        current = getattr(character, stat)
        setattr(character, stat, current + value)


def get_random_upgrades(n=3):
    choices = UPGRADES[:]
    selected = []

    for _ in range(n):
        total = sum(u["weight"] for u in choices)
        pick = random.uniform(0, total)

        upto = 0
        for u in choices:
            upto += u["weight"]
            if upto >= pick:
                selected.append(u)
                choices.remove(u)
                break

    return selected
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


def apply_upgrade(self, upgrade):
    t = upgrade.get("stat")
    value = upgrade["value"]

    # HP
    if t == "hp":
        self.max_hp += value
        self.hp += value
        return

    # DAMAGE (min/max split)
    if t == "atk":
        self.atk_min += value[0]
        self.atk_max += value[1]
        return

    # CRIT
    if t == "crit":
        self.crit += value
        return

    # DODGE
    if t == "dodge":
        self.dodge += value
        return

    # LIFESTEAL
    if t == "lifesteal":
        self.lifesteal += value
        return

    # ATTACK SPEED
    if t == "attack_speed":
        self.attack_speed += value
        return

    # ARMOR
    if t == "armor":
        self.armor += value
        return


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
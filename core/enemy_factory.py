import random
from core.character_factory import build_character
from core.characters import CHARACTERS


def scale_value(value, round_number, growth=0.08):
    return int(value * (1 + round_number * growth))


def generate_enemy(round_number):
    base = random.choice(CHARACTERS)

    # copy base so we don’t mutate original
    enemy_data = dict(base)

    # -------------------------
    # SCALE CORE STATS
    # -------------------------
    enemy_data["hp"] = scale_value(enemy_data["hp"], round_number)
    enemy_data["atk_min"] = scale_value(enemy_data["atk_min"], round_number)
    enemy_data["atk_max"] = scale_value(enemy_data["atk_max"], round_number)

    enemy_data["armor"] = scale_value(enemy_data.get("armor", 0), round_number)
    enemy_data["magic_resist"] = scale_value(enemy_data.get("magic_resist", 0), round_number)

    # -------------------------
    # SLIGHT RANDOM VARIANCE (keeps fights fresh)
    # -------------------------
    enemy_data["hp"] = int(enemy_data["hp"] * random.uniform(0.9, 1.1))
    enemy_data["atk_min"] = int(enemy_data["atk_min"] * random.uniform(0.9, 1.1))
    enemy_data["atk_max"] = int(enemy_data["atk_max"] * random.uniform(0.9, 1.2))

    # -------------------------
    # POSITION + COLOR OVERRIDE FOR ENEMY SIDE
    # -------------------------
    enemy_data["x"] = 650
    enemy_data["y"] = 250

    # optional enemy tint (keeps readability)
    enemy_data["color"] = (255, 80, 80)

    # IMPORTANT: reuse full character pipeline
    return build_character(enemy_data)
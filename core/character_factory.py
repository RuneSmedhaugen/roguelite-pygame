from core.character_data import CharacterData
from core.entities import Character
import random
from core.characters import CHARACTERS

def get_random_characters(n=5):
    return random.sample(CHARACTERS, n)

def build_character(raw, x=150, y=250, scale=1.0):
    passive = raw.get("passive")
    passives = []

    if passive:
        if isinstance(passive, list):
            passives = passive
        else:
            passives = [passive]

    data = CharacterData(
        x=x,
        y=y,
        hp=int(raw["hp"] * scale),
        atk_min=int(raw["atk_min"] * scale),
        atk_max=int(raw["atk_max"] * scale),
        crit=raw.get("crit", 0),
        dodge=raw.get("dodge", 0),
        lifesteal=raw.get("lifesteal", 0),
        attack_speed=raw.get("attack_speed", 1.0),
        armor=int(raw.get("armor", 0) * scale),
        magic_resist=raw.get("magic_resist", 0),
        magic_damage=raw.get("magic_damage", 0.0),
        hp_growth=raw.get("hp_growth", 0),
        atk_growth=raw.get("atk_growth", 0),
        size=raw.get("size", 1.0),
        main_stat=raw.get("main_stat"),
        rarity=raw.get("rarity", "common"),
        name=raw["name"],
        character_id=raw.get("id", raw["name"].lower().replace(" ", "_")),
        sprite_name=raw.get("sprite"),
        intro_sound=raw.get("intro_sound"),
        win_sound=raw.get("win_sound"),
        lose_sound=raw.get("lose_sound"),
        passives=passives
    )

    return Character(data)

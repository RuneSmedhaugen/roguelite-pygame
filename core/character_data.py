from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CharacterData:
    x: int
    y: int

    hp: int
    atk_min: int
    atk_max: int

    crit: float = 0.0
    dodge: float = 0.0
    lifesteal: float = 0.0
    attack_speed: float = 1.0

    armor: int = 0
    magic_resist: int = 0
    magic_damage: float = 0.0

    hp_growth: int = 0
    atk_growth: int = 0

    size: float = 1.0
    main_stat: str = None
    rarity: str = "common"

    name: str = "Unknown"
    sprite_name: str = None

    passives: List[str] = None
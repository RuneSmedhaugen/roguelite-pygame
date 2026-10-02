from core.passives import create_passive


class Character:
    def __init__(self, data):
        self.x = data.x
        self.y = data.y

        self.hp = data.hp
        self.max_hp = data.hp

        self.atk_min = data.atk_min
        self.atk_max = data.atk_max

        self.crit = data.crit
        self.dodge = data.dodge
        self.lifesteal = data.lifesteal
        self.attack_speed = data.attack_speed

        self.armor = data.armor
        self.magic_resist = data.magic_resist
        self.magic_damage = data.magic_damage

        self.hp_growth = data.hp_growth
        self.atk_growth = data.atk_growth

        self.size = data.size
        self.main_stat = data.main_stat
        self.rarity = data.rarity

        self.name = data.name
        self.sprite_name = data.sprite_name

        self.passives = []

        passive_ids = data.passives or []

        for pid in passive_ids:
            self.passives.append(create_passive(pid))

    
    def is_alive(self):
        return self.hp > 0

    def apply_upgrade(self, upgrade):
        stat = upgrade.get("stat")
        value = upgrade.get("value")

        # -------- HP --------
        if stat == "hp":
            self.max_hp += value
            self.hp += value
            return

        # -------- DAMAGE --------
        if stat == "atk":
            min_inc, max_inc = value
            self.atk_min += min_inc
            self.atk_max += max_inc
            return

        # -------- GENERIC STATS --------
        if hasattr(self, stat):
            current = getattr(self, stat)
            setattr(self, stat, current + value)

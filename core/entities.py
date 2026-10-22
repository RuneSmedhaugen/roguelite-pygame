from core.passives import create_passive
from core.upgrades import apply_upgrade


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
        self.character_id = data.character_id
        self.sprite_name = data.sprite_name
        self.intro_sound = data.intro_sound
        self.win_sound = data.win_sound
        self.lose_sound = data.lose_sound

        self.passives = []
        self.status_effects = []

        passive_ids = data.passives or []

        for pid in passive_ids:
            self.passives.append(create_passive(pid))

    
    def is_alive(self):
        return self.hp > 0

    def apply_status(self, name, duration, dps, stacks=1):
        """Apply or refresh a short damage-over-time effect."""
        matching = next(
            (effect for effect in self.status_effects if effect["name"] == name and effect["dps"] == dps),
            None,
        )
        if matching is None:
            self.status_effects.append({
                "name": name,
                "duration": duration,
                "dps": dps,
                "stacks": stacks,
                "tick": 0.0,
            })
        else:
            matching["duration"] = max(matching["duration"], duration)
            matching["stacks"] = min(9, matching["stacks"] + stacks)

    def update_status_effects(self, dt):
        damage_events = []
        active_effects = []
        for effect in self.status_effects:
            effect["duration"] -= dt
            effect["tick"] += dt
            while effect["tick"] >= 1.0 and effect["duration"] >= -1e-6:
                effect["tick"] -= 1.0
                damage = min(self.hp, effect["dps"] * effect["stacks"])
                if damage > 0:
                    self.hp -= damage
                    damage_events.append({
                        "kind": "damage",
                        "character": self,
                        "amount": damage,
                        "label": f"BLEED -{round(damage)}",
                    })
                if self.hp <= 0:
                    self.hp = 0
                    break
            if effect["duration"] > 0 and self.hp > 0:
                active_effects.append(effect)
        self.status_effects = active_effects
        return damage_events

    def apply_upgrade(self, upgrade):
        apply_upgrade(self, upgrade)

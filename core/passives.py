import random


# =========================================================
# BASE PASSIVE
# =========================================================

class Passive:
    def notify(self, message):
        if not hasattr(self, "_notifications"):
            self._notifications = []
        self._notifications.append(message)

    def take_notifications(self):
        notifications = getattr(self, "_notifications", [])
        self._notifications = []
        return notifications

    def status_text(self, unit):
        return "Passive active"

    def on_combat_start(self, unit): pass
    def on_combat_end(self, unit): pass

    def on_hit_taken(self, unit, attacker, dmg): return dmg
    def on_hit_dealt(self, unit, target, dmg): return dmg

    def on_tick(self, unit, dt): pass

    def modify_damage_taken(self, unit, dmg): return dmg
    def modify_damage_dealt(self, unit, dmg): return dmg

    def modify_crit(self, unit, crit): return crit
    def modify_attack(self, unit, atk): return atk
    def modify_armor(self, unit, armor): return armor
    def modify_attack_speed(self, unit, speed): return speed
    def modify_lifesteal(self, unit, ls): return ls

    def modify_dodge(self, unit, dodge): return dodge

    def modify_stats(self, unit, stats): return stats

    def on_dodge(self, unit): pass
    def on_crit(self, unit, target, dmg): pass
    


# =========================================================
# PASSIVES
# =========================================================

class ScalingShieldPassive(Passive):
    def __init__(self, value=0.02, cap=0.25):
        self.value = value
        self.cap = cap
        self.current_bonus = 0.0
        self.in_combat = False

    def on_combat_start(self, unit):
        self.in_combat = True
        self.current_bonus = 0.0

    def on_combat_end(self, unit):
        self.in_combat = False

    def on_tick(self, unit, dt):
        if not self.in_combat:
            return
        self.current_bonus = min(self.cap, self.current_bonus + self.value * dt)

    def modify_damage_taken(self, unit, dmg):
        return max(0, dmg * (1.0 - self.current_bonus))

    def status_text(self, unit):
        return f"Damage reduction {self.current_bonus:.0%} / {self.cap:.0%}"


class DoubleStrikePassive(Passive):
    def __init__(self, chance=0.2, damage_mult=0.5):
        self.chance = chance
        self.damage_mult = damage_mult

    def on_hit_dealt(self, unit, target, dmg):
        if random.random() < self.chance:
            bonus = dmg * self.damage_mult
            self.notify(f"BONUS HIT! +{round(bonus)} damage")
            return dmg + bonus
        return dmg

    def status_text(self, unit):
        return f"{self.chance:.0%} chance for +{self.damage_mult:.0%} hit damage"


class EvasiveFocusPassive(Passive):
    def __init__(self, bonus_crit_after_dodge=0.25, duration_ms=3000):
        self.bonus = bonus_crit_after_dodge
        self.duration = duration_ms / 1000
        self.timer = 0

    def on_combat_start(self, unit):
        self.timer = 0

    def on_dodge(self, unit):
        self.timer = self.duration
        self.notify("EVASIVE FOCUS! +25% crit")

    def on_tick(self, unit, dt):
        self.timer = max(0, self.timer - dt)

    def modify_crit(self, unit, crit):
        return crit + self.bonus if self.timer > 0 else crit

    def status_text(self, unit):
        return f"Crit +{self.bonus:.0%} for {self.timer:.1f}s" if self.timer > 0 else "Waiting for a dodge"


class RampArmorPassive(Passive):
    def __init__(self, gain_per_hit=1, cap=20):
        self.gain = gain_per_hit
        self.cap = cap
        self.current = 0

    def on_combat_start(self, unit):
        self.current = 0

    def on_hit_taken(self, unit, attacker, dmg):
        previous = self.current
        self.current = min(self.cap, self.current + self.gain)
        if self.current > previous:
            self.notify(f"RAMP ARMOR! +{self.gain} armor ({self.current}/{self.cap})")
        return dmg

    def modify_armor(self, unit, armor):
        return armor + self.current

    def status_text(self, unit):
        return f"Bonus armor +{self.current} / +{self.cap}"


class LowHpCritScalingPassive(Passive):
    def __init__(self, max_bonus=0.4):
        self.max_bonus = max_bonus

    def modify_crit(self, unit, crit):
        hp_ratio = unit.hp / unit.max_hp
        bonus = (1.0 - hp_ratio) * self.max_bonus
        return crit + bonus

    def status_text(self, unit):
        bonus = (1.0 - max(0, unit.hp) / unit.max_hp) * self.max_bonus
        return f"Bonus crit +{bonus:.0%} (scales with missing health)"


class RegenOnDamagePassive(Passive):
    def __init__(self, heal_percent=0.03):
        self.heal_percent = heal_percent

    def on_hit_taken(self, unit, attacker, dmg):
        heal = dmg * self.heal_percent
        before = unit.hp
        unit.hp = min(unit.max_hp, unit.hp + heal)
        actual_heal = unit.hp - before
        if actual_heal > 0:
            self.notify(f"REGEN! +{round(actual_heal, 1)} HP")
        return dmg

    def status_text(self, unit):
        return f"Recover {self.heal_percent:.0%} of damage taken"


class EveryNthHitCritPassive(Passive):
    def __init__(self, every=3):
        self.every = every
        self.counter = 0

    def on_combat_start(self, unit):
        self.counter = 0

    def on_hit_dealt(self, unit, target, dmg):
        self.counter += 1
        if self.counter % self.every == 0:
            self.notify(f"{self.every}RD HIT! DOUBLE DAMAGE")
            return dmg * 2
        return dmg

    def status_text(self, unit):
        return f"Next hit {self.every - self.counter % self.every}/{self.every} is double damage"


class BleedOnHitPassive(Passive):
    def __init__(self, stack=3, damage_per_stack=1, duration=3):
        self.stack = stack
        self.dps = damage_per_stack
        self.duration = duration

    def on_hit_dealt(self, unit, target, dmg):
        if hasattr(target, "apply_status"):
            target.apply_status("bleed", stacks=self.stack, dps=self.dps, duration=self.duration)
            self.notify(f"BLEED! {self.stack} stacks")
        return dmg

    def status_text(self, unit):
        return f"Hits apply {self.stack} bleed stacks"


class LifestealScalingLowHpPassive(Passive):
    def __init__(self, bonus_max=0.25):
        self.bonus_max = bonus_max

    def modify_lifesteal(self, unit, ls):
        hp_ratio = unit.hp / unit.max_hp
        bonus = (1.0 - hp_ratio) * self.bonus_max
        return ls + bonus

    def status_text(self, unit):
        bonus = (1.0 - max(0, unit.hp) / unit.max_hp) * self.bonus_max
        return f"Bonus lifesteal +{bonus:.0%} (scales with missing health)"


class DamageReductionScalingFightTimePassive(Passive):
    def __init__(self, max_reduction=0.3):
        self.max = max_reduction
        self.time = 0

    def on_combat_start(self, unit):
        self.time = 0

    def on_tick(self, unit, dt):
        self.time += dt

    def modify_damage_taken(self, unit, dmg):
        reduction = min(self.max, self.time * 0.01)
        return dmg * (1.0 - reduction)

    def status_text(self, unit):
        return f"Damage reduction {min(self.max, self.time * 0.01):.0%} / {self.max:.0%}"


class SpeedOnDodgePassive(Passive):
    def __init__(self, attack_speed_bonus=0.2, duration_ms=2000):
        self.bonus = attack_speed_bonus
        self.duration = duration_ms / 1000
        self.timer = 0

    def on_combat_start(self, unit):
        self.timer = 0

    def on_dodge(self, unit):
        self.timer = self.duration
        self.notify("DODGE BOOST! +20% attack speed")

    def on_tick(self, unit, dt):
        self.timer = max(0, self.timer - dt)

    def modify_attack_speed(self, unit, speed):
        return speed + self.bonus if self.timer > 0 else speed

    def status_text(self, unit):
        return f"Attack speed +{self.bonus:.1f} for {self.timer:.1f}s" if self.timer > 0 else "Waiting for a dodge"


class PureCritSpikePassive(Passive):
    def __init__(self, crit_bonus_cap=0.5):
        self.cap = crit_bonus_cap

    def modify_crit(self, unit, crit):
        return crit + random.uniform(0, self.cap)

    def status_text(self, unit):
        return f"Each attack rolls up to +{self.cap:.0%} crit"


class ArmorToDamagePassive(Passive):
    def __init__(self, ratio=0.1):
        self.ratio = ratio

    def modify_damage_dealt(self, unit, dmg):
        return dmg + unit.armor * self.ratio

    def status_text(self, unit):
        return f"Bonus damage +{unit.armor * self.ratio:.1f} from armor"


class ToggleModePassive(Passive):
    def __init__(self, cycle_ms=3000, on_bonus_atk=0.3, off_bonus_armor=0.3):
        self.cycle = cycle_ms / 1000
        self.on_bonus = on_bonus_atk
        self.off_bonus = off_bonus_armor
        self.timer = 0
        self.state = True

    def on_combat_start(self, unit):
        self.timer = 0
        self.state = True

    def on_tick(self, unit, dt):
        self.timer += dt
        if self.timer >= self.cycle:
            self.timer -= self.cycle
            self.state = not self.state
            self.notify("ONOFF: ATTACK STANCE" if self.state else "ONOFF: ARMOR STANCE")

    def status_text(self, unit):
        remaining = max(0, self.cycle - self.timer)
        if self.state:
            return f"ON: +{self.on_bonus:.0%} attack  •  switches in {remaining:.1f}s"
        return f"OFF: +{self.off_bonus:.0%} armor  •  switches in {remaining:.1f}s"

    def modify_attack(self, unit, atk):
        return atk * (1.0 + self.on_bonus) if self.state else atk

    def modify_armor(self, unit, armor):
        return armor * (1.0 + self.off_bonus) if not self.state else armor

class AdaptiveStatBoostPassive(Passive):
    def __init__(self, interval_ms=4000):
        self.interval = interval_ms / 1000
        self.timer = 0
        self.buff = None

    def on_combat_start(self, unit):
        self.timer = 0
        self.buff = None

    def on_tick(self, unit, dt):
        self.timer += dt
        if self.timer >= self.interval:
            self.timer -= self.interval
            previous = self.buff
            self.buff = random.choice(["hp", "atk", "armor", "dodge"])
            if self.buff == "hp":
                heal = unit.max_hp * 0.1
                before = unit.hp
                unit.hp = min(unit.max_hp, unit.hp + heal)
                actual_heal = unit.hp - before
                self.notify(f"HEALTH SURGE! +{round(actual_heal, 1)} HP")
            elif self.buff != previous:
                self.notify(f"ADAPTIVE BOOST! {self.buff.upper()} +10%")

    def modify_stats(self, unit, stats):
        if self.buff in stats:
            stats[self.buff] *= 1.1
        return stats

    def status_text(self, unit):
        remaining = max(0, self.interval - self.timer)
        if self.buff == "hp":
            return "HP SURGE: one-time heal"
        return f"{self.buff.upper()} +10% for {remaining:.1f}s" if self.buff else f"Random boost in {remaining:.1f}s"


class BleedOnCritPassive(Passive):
    def __init__(self, bleed_duration=3):
        self.duration = bleed_duration

    def on_crit(self, unit, target, dmg):
        if hasattr(target, "apply_status"):
            target.apply_status("bleed", duration=self.duration, dps=2)
            self.notify(f"CRITICAL BLEED! {self.duration}s")

    def status_text(self, unit):
        return f"Critical hits apply {self.duration}s bleed"


class RandomStatSurgePassive(Passive):
    def __init__(self, interval_ms=5000):
        self.interval = interval_ms / 1000
        self.timer = 0
        self.buff = None

    def on_combat_start(self, unit):
        self.timer = 0
        self.buff = None

    def on_tick(self, unit, dt):
        self.timer += dt
        if self.timer >= self.interval:
            self.timer -= self.interval
            self.buff = random.choice(["crit", "atk", "lifesteal", "dodge"])
            self.notify(f"RANDOM SURGE! {self.buff.upper()} boosted")

    def modify_stats(self, unit, stats):
        if self.buff in stats:
            stats[self.buff] *= 1.15
        return stats

    def status_text(self, unit):
        remaining = max(0, self.interval - self.timer)
        return f"{self.buff.upper()} +15% for {remaining:.1f}s" if self.buff else f"Random surge in {remaining:.1f}s"


class DodgeSpeedStackingPassive(Passive):
    def __init__(self, max_stacks=5, bonus_per_stack=0.05):
        self.stacks = 0
        self.max_stacks = max_stacks
        self.bonus = bonus_per_stack

    def on_combat_start(self, unit):
        self.stacks = 0

    def on_dodge(self, unit):
        previous = self.stacks
        self.stacks = min(self.max_stacks, self.stacks + 1)
        if self.stacks > previous:
            self.notify(f"DODGE STACK! {self.stacks}/{self.max_stacks}")

    def on_tick(self, unit, dt):
        self.stacks = max(0, self.stacks - dt * 1.5)

    def modify_attack_speed(self, unit, speed):
        return speed * (1.0 + self.stacks * self.bonus)

    def status_text(self, unit):
        return f"Attack speed +{self.stacks * self.bonus:.0%} ({self.stacks:.1f}/{self.max_stacks} stacks)"


# =========================================================
# REGISTRY
# =========================================================

PASSIVE_REGISTRY = {
    "dodge_speed_stacking": DodgeSpeedStackingPassive,
    "scaling_shield": ScalingShieldPassive,
    "double_strike": DoubleStrikePassive,
    "evasive_focus": EvasiveFocusPassive,
    "ramp_armor": RampArmorPassive,
    "low_hp_crit_scaling": LowHpCritScalingPassive,
    "regen_on_damage": RegenOnDamagePassive,
    "nth_hit_crit": EveryNthHitCritPassive,
    "bleed_on_hit": BleedOnHitPassive,
    "lifesteal_scaling_low_hp": LifestealScalingLowHpPassive,
    "damage_reduction_fight_scaling": DamageReductionScalingFightTimePassive,
    "speed_on_dodge": SpeedOnDodgePassive,
    "pure_crit_spike": PureCritSpikePassive,
    "armor_to_damage": ArmorToDamagePassive,
    "toggle_mode": ToggleModePassive,
    "adaptive_boost": AdaptiveStatBoostPassive,
    "bleed_on_crit": BleedOnCritPassive,
    "random_surge": RandomStatSurgePassive,
}


PASSIVE_INFO = {
    "scaling_shield": ("Scaling Shield", "Gain 2% damage reduction each second, up to 25%. It resets at the start of each battle."),
    "double_strike": ("Double Strike", "Each hit has a 20% chance to deal 50% bonus damage."),
    "evasive_focus": ("Evasive Focus", "After dodging, gain 25 percentage points of critical chance for 3 seconds."),
    "ramp_armor": ("Ramp Armor", "Each time you are hit, gain 1 armor for the rest of the battle, up to 20."),
    "low_hp_crit_scaling": ("Desperation Crits", "Critical chance rises as health falls, reaching up to 40 percentage points at critical health."),
    "regen_on_damage": ("Damage Regeneration", "Recover 3% of the damage you take, after damage reduction."),
    "nth_hit_crit": ("Every Third Hit", "Every third hit that connects deals double damage."),
    "bleed_on_hit": ("Bleeding Strikes", "Each hit applies a 3-second bleed dealing 3 damage per second."),
    "lifesteal_scaling_low_hp": ("Desperate Lifesteal", "Lifesteal increases as health falls, by up to 25 percentage points."),
    "damage_reduction_fight_scaling": ("Stubborn Defense", "Gain 1% damage reduction per second in a fight, up to 30%."),
    "speed_on_dodge": ("Dodge Tempo", "After dodging, attack 0.2 times per second faster for 2 seconds."),
    "pure_crit_spike": ("Wild Criticals", "Each attack gains a random 0–50 percentage points of critical chance."),
    "armor_to_damage": ("Armor Slam", "Add damage equal to 10% of your armor to every hit."),
    "toggle_mode": ("On / Off Stances", "Switch every 3 seconds: On gives 30% more attack; Off gives 30% more armor."),
    "adaptive_boost": ("Adaptive Boost", "Every 4 seconds, randomly boost attack, armor, or dodge by 10%, or heal 10% of max health."),
    "bleed_on_crit": ("Critical Bleed", "Critical hits apply a 3-second bleed dealing 2 damage per second."),
    "random_surge": ("Random Surge", "Every 5 seconds, randomly boost critical chance, attack, lifesteal, or dodge by 15%."),
    "dodge_speed_stacking": ("Dodge Momentum", "Dodging builds up to 5 attack-speed stacks. Each adds 5%; stacks fade over time."),
}


def create_passive(passive_id, **kwargs):
    cls = PASSIVE_REGISTRY.get(passive_id)
    if not cls:
        raise ValueError(f"Unknown passive: {passive_id}")
    passive = cls(**kwargs)
    passive.passive_id = passive_id
    return passive

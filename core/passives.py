import random


# =========================================================
# BASE PASSIVE
# =========================================================

class Passive:
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


class DoubleStrikePassive(Passive):
    def __init__(self, chance=0.2, damage_mult=0.5):
        self.chance = chance
        self.damage_mult = damage_mult

    def on_hit_dealt(self, unit, target, dmg):
        if random.random() < self.chance:
            return dmg + (dmg * self.damage_mult)
        return dmg


class EvasiveFocusPassive(Passive):
    def __init__(self, bonus_crit_after_dodge=0.25, duration_ms=3000):
        self.bonus = bonus_crit_after_dodge
        self.duration = duration_ms / 1000
        self.timer = 0

    def on_dodge(self, unit):
        self.timer = self.duration

    def on_tick(self, unit, dt):
        self.timer = max(0, self.timer - dt)

    def modify_crit(self, unit, crit):
        return crit + self.bonus if self.timer > 0 else crit


class RampArmorPassive(Passive):
    def __init__(self, gain_per_hit=1, cap=20):
        self.gain = gain_per_hit
        self.cap = cap
        self.current = 0

    def on_hit_taken(self, unit, attacker, dmg):
        self.current = min(self.cap, self.current + self.gain)
        return dmg

    def modify_armor(self, unit, armor):
        return armor + self.current


class LowHpCritScalingPassive(Passive):
    def __init__(self, max_bonus=0.4):
        self.max_bonus = max_bonus

    def modify_crit(self, unit, crit):
        hp_ratio = unit.hp / unit.max_hp
        bonus = (1.0 - hp_ratio) * self.max_bonus
        return crit + bonus


class RegenOnDamagePassive(Passive):
    def __init__(self, heal_percent=0.03):
        self.heal_percent = heal_percent

    def on_hit_taken(self, unit, attacker, dmg):
        heal = dmg * self.heal_percent
        unit.hp = min(unit.max_hp, unit.hp + heal)
        return dmg


class EveryNthHitCritPassive(Passive):
    def __init__(self, every=3):
        self.every = every
        self.counter = 0

    def on_hit_dealt(self, unit, target, dmg):
        self.counter += 1
        if self.counter % self.every == 0:
            return dmg * 2
        return dmg


class BleedOnHitPassive(Passive):
    def __init__(self, stack=3, damage_per_stack=1):
        self.stack = stack
        self.dps = damage_per_stack

    def on_hit_dealt(self, unit, target, dmg):
        if hasattr(target, "apply_status"):
            target.apply_status("bleed", stacks=self.stack, dps=self.dps)
        return dmg


class LifestealScalingLowHpPassive(Passive):
    def __init__(self, bonus_max=0.25):
        self.bonus_max = bonus_max

    def modify_lifesteal(self, unit, ls):
        hp_ratio = unit.hp / unit.max_hp
        bonus = (1.0 - hp_ratio) * self.bonus_max
        return ls + bonus


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


class SpeedOnDodgePassive(Passive):
    def __init__(self, attack_speed_bonus=0.2, duration_ms=2000):
        self.bonus = attack_speed_bonus
        self.duration = duration_ms / 1000
        self.timer = 0

    def on_dodge(self, unit):
        self.timer = self.duration

    def on_tick(self, unit, dt):
        self.timer = max(0, self.timer - dt)

    def modify_attack_speed(self, unit, speed):
        return speed + self.bonus if self.timer > 0 else speed


class PureCritSpikePassive(Passive):
    def __init__(self, crit_bonus_cap=0.5):
        self.cap = crit_bonus_cap

    def modify_crit(self, unit, crit):
        return crit + random.uniform(0, self.cap)


class ArmorToDamagePassive(Passive):
    def __init__(self, ratio=0.1):
        self.ratio = ratio

    def modify_damage_dealt(self, unit, dmg):
        return dmg + unit.armor * self.ratio


class ToggleModePassive(Passive):
    def __init__(self, cycle_ms=3000, on_bonus_atk=0.3, off_bonus_armor=0.3):
        self.cycle = cycle_ms / 1000
        self.on_bonus = on_bonus_atk
        self.off_bonus = off_bonus_armor
        self.timer = 0
        self.state = True

    def on_tick(self, unit, dt):
        self.timer += dt
        if self.timer >= self.cycle:
            self.timer = 0
            self.state = not self.state

    def modify_attack(self, unit, atk):
        return atk * (1.0 + self.on_bonus) if self.state else atk

    def modify_armor(self, unit, armor):
        return armor * (1.0 + self.off_bonus) if not self.state else armor


class AdaptiveStatBoostPassive(Passive):
    def __init__(self, interval_ms=4000):
        self.interval = interval_ms / 1000
        self.timer = 0
        self.buff = None

    def on_tick(self, unit, dt):
        self.timer += dt
        if self.timer >= self.interval:
            self.timer = 0
            self.buff = random.choice(["hp", "atk", "armor", "dodge"])

    def modify_stats(self, unit, stats):
        if self.buff in stats:
            stats[self.buff] *= 1.1
        return stats


class BleedOnCritPassive(Passive):
    def __init__(self, bleed_duration=3):
        self.duration = bleed_duration

    def on_crit(self, unit, target, dmg):
        if hasattr(target, "apply_status"):
            target.apply_status("bleed", duration=self.duration, dps=2)


class RandomStatSurgePassive(Passive):
    def __init__(self, interval_ms=5000):
        self.interval = interval_ms / 1000
        self.timer = 0
        self.buff = None

    def on_tick(self, unit, dt):
        self.timer += dt
        if self.timer >= self.interval:
            self.timer = 0
            self.buff = random.choice(["crit", "atk", "lifesteal", "dodge"])

    def modify_stats(self, unit, stats):
        if self.buff in stats:
            stats[self.buff] *= 1.15
        return stats


class DodgeSpeedStackingPassive(Passive):
    def __init__(self, max_stacks=5, bonus_per_stack=0.05):
        self.stacks = 0
        self.max_stacks = max_stacks
        self.bonus = bonus_per_stack

    def on_dodge(self, unit):
        self.stacks = min(self.max_stacks, self.stacks + 1)

    def on_tick(self, unit, dt):
        self.stacks = max(0, self.stacks - dt * 1.5)

    def modify_attack_speed(self, unit, speed):
        return speed * (1.0 + self.stacks * self.bonus)


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


def create_passive(passive_id, **kwargs):
    cls = PASSIVE_REGISTRY.get(passive_id)
    if not cls:
        raise ValueError(f"Unknown passive: {passive_id}")
    return cls(**kwargs)
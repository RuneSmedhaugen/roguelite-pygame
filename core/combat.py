import random


class CombatEngine:

    def resolve_defense_stats(self, unit):
        stats = {"armor": unit.armor, "dodge": unit.dodge}
        for passive in unit.passives:
            stats = passive.modify_stats(unit, stats)
        for passive in unit.passives:
            stats["armor"] = passive.modify_armor(unit, stats["armor"])
            stats["dodge"] = passive.modify_dodge(unit, stats["dodge"])
        stats["armor"] = max(0, stats["armor"])
        stats["dodge"] = min(max(stats["dodge"], 0), 0.95)
        return stats

    def resolve_attack_speed(self, unit):
        speed = unit.attack_speed
        for passive in unit.passives:
            speed = passive.modify_attack_speed(unit, speed)
        return max(0.1, speed)

    def resolve_display_stats(self, unit):
        """Return current passive-adjusted values without consuming combat RNG."""
        def modified_attack(base_attack):
            stats = {
                "atk": base_attack,
                "crit": unit.crit,
                "armor": unit.armor,
                "speed": unit.attack_speed,
                "lifesteal": unit.lifesteal,
                "dodge": unit.dodge,
            }
            for passive in unit.passives:
                stats = passive.modify_stats(unit, stats)
            attack = stats["atk"]
            for passive in unit.passives:
                attack = passive.modify_attack(unit, attack)
            for passive in unit.passives:
                attack = passive.modify_damage_dealt(unit, attack)
            return attack

        stats = {"atk": unit.atk_min, "crit": unit.crit, "armor": unit.armor,
                 "speed": unit.attack_speed, "lifesteal": unit.lifesteal, "dodge": unit.dodge}
        for passive in unit.passives:
            stats = passive.modify_stats(unit, stats)

        crit_min = crit_max = stats["crit"]
        lifesteal = stats["lifesteal"]
        for passive in unit.passives:
            if getattr(passive, "passive_id", None) == "pure_crit_spike":
                crit_max += passive.cap
            else:
                crit_min = passive.modify_crit(unit, crit_min)
                crit_max = passive.modify_crit(unit, crit_max)
            lifesteal = passive.modify_lifesteal(unit, lifesteal)

        defense = self.resolve_defense_stats(unit)
        return {
            "hp": unit.hp,
            "max_hp": unit.max_hp,
            "atk_min": modified_attack(unit.atk_min),
            "atk_max": modified_attack(unit.atk_max),
            "speed": self.resolve_attack_speed(unit),
            "crit_min": min(max(crit_min, 0), 0.95),
            "crit_max": min(max(crit_max, 0), 0.95),
            "dodge": defense["dodge"],
            "lifesteal": lifesteal,
            "armor": defense["armor"],
        }

    @staticmethod
    def _passive_events(units):
        events = []
        seen = set()
        for unit in units:
            if id(unit) in seen:
                continue
            seen.add(id(unit))
            for passive in unit.passives:
                for message in passive.take_notifications():
                    events.append({"kind": "passive", "character": unit, "label": message})
        return events

    def resolve_attack_stats(self, attacker):

        base_stats = {
            "atk": random.randint(attacker.atk_min, attacker.atk_max),
            "crit": attacker.crit,
            "armor": attacker.armor,
            "speed": attacker.attack_speed,
            "lifesteal": attacker.lifesteal,
            "dodge": attacker.dodge
        }

        # 1. global stat modifier pass (ONLY ONCE)
        for p in attacker.passives:
            base_stats = p.modify_stats(attacker, base_stats)

        # 2. per-stat modifiers (stable order, no duplication)
        for p in attacker.passives:
            base_stats["atk"] = p.modify_attack(attacker, base_stats["atk"])
            base_stats["crit"] = p.modify_crit(attacker, base_stats["crit"])
            base_stats["armor"] = p.modify_armor(attacker, base_stats["armor"])
            base_stats["speed"] = p.modify_attack_speed(attacker, base_stats["speed"])
            base_stats["lifesteal"] = p.modify_lifesteal(attacker, base_stats["lifesteal"])
            base_stats["dodge"] = p.modify_dodge(attacker, base_stats["dodge"])

        # clamp safety (prevents broken builds)
        base_stats["crit"] = min(max(base_stats["crit"], 0), 0.95)
        base_stats["dodge"] = min(max(base_stats["dodge"], 0), 0.95)

        return base_stats

    # --------------------------------------------------------

    def hit(self, attacker, target, atk_stats=None, def_stats=None):

        if not attacker.is_alive() or not target.is_alive():
            return []

        # -------------------------
        # STAT SNAPSHOTS (single source per hit)
        # -------------------------
        atk_stats = atk_stats or self.resolve_attack_stats(attacker)

        # minimal & stable defense stats (no RNG reuse bug)
        def_stats = def_stats or self.resolve_defense_stats(target)

        # -------------------------
        # 1. DODGE CHECK
        # -------------------------
        if random.random() < def_stats["dodge"]:
            for p in target.passives:
                p.on_dodge(target)
            return [{"kind": "dodge", "character": target}, *self._passive_events((target,))]

        # -------------------------
        # 2. BASE DAMAGE
        # -------------------------
        dmg = atk_stats["atk"]

        # -------------------------
        # 3. CRIT
        # -------------------------
        is_crit = random.random() < atk_stats["crit"]
        if is_crit:
            dmg *= 2

        # -------------------------
        # 4. ATTACKER MODIFIERS
        # -------------------------
        for p in attacker.passives:
            dmg = p.modify_damage_dealt(attacker, dmg)

        # Hit callbacks may alter damage; apply their result before mitigation.
        for p in attacker.passives:
            dmg = p.on_hit_dealt(attacker, target, dmg)

        # -------------------------
        # 5. TARGET MITIGATION
        # -------------------------
        for p in target.passives:
            dmg = p.modify_damage_taken(target, dmg)

        damage_after_passives = max(0, dmg)
        armor_reduction = max(0, def_stats["armor"] * 0.3)
        armor_blocked = min(damage_after_passives, armor_reduction)

        # -------------------------
        # 6. ARMOR REDUCTION
        # -------------------------
        dmg = max(0, damage_after_passives - armor_reduction)

        # -------------------------
        # 7. APPLY DAMAGE
        # -------------------------
        target.hp -= dmg

        # -------------------------
        # 8. PASSIVE REACTIONS
        # -------------------------
        for p in target.passives:
            p.on_hit_taken(target, attacker, dmg)

        if is_crit:
            for p in attacker.passives:
                p.on_crit(attacker, target, dmg)

        # -------------------------
        # 9. LIFESTEAL
        # -------------------------
        heal = dmg * atk_stats["lifesteal"]
        hp_before_heal = attacker.hp
        attacker.hp = min(attacker.max_hp, attacker.hp + heal)
        actual_heal = attacker.hp - hp_before_heal

        # -------------------------
        # 10. DEATH CHECK (FIXED)
        # -------------------------
        if target.hp <= 0:
            target.hp = 0

        events = []
        if dmg > 0:
            events.append({"kind": "critical" if is_crit else "damage", "character": target, "amount": dmg})
        if armor_blocked > 0:
            events.append({"kind": "block", "character": target, "amount": armor_blocked})
        if actual_heal > 0:
            events.append({"kind": "heal", "character": attacker, "amount": actual_heal})
        events.extend(self._passive_events((attacker, target)))
        return events

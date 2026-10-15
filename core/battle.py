import pygame
import random

from ui.draw import get_sprite
from ui.layout import ui_scale
from ui.combat_text import FloatingCombatText


# ------------------------------------------------------------
# COMBAT ENGINE
# ------------------------------------------------------------

class CombatEngine:

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
        def_stats = def_stats or {
            "dodge": target.dodge,
            "armor": target.armor
        }

        # -------------------------
        # 1. DODGE CHECK
        # -------------------------
        if random.random() < def_stats["dodge"]:
            for p in target.passives:
                p.on_dodge(target)
            return [{"kind": "dodge", "character": target}]

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

        for p in attacker.passives:
            p.on_hit_dealt(attacker, target, dmg)

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
        return events


# ------------------------------------------------------------
# BATTLE LOOP
# ------------------------------------------------------------

class Battle:

    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

        self.finished = False
        self.winner = None

        self.combat = CombatEngine()
        self.combat_texts = []

        self.player_last_attack = 0
        self.enemy_last_attack = 0

        # combat start hooks
        for unit in (self.player, self.enemy):
            for p in unit.passives:
                p.on_combat_start(unit)

    # --------------------------------------------------------

    def update(self):

        now = pygame.time.get_ticks()
        self.combat_texts = [
            item for item in self.combat_texts
            if now - item.created_at < item.duration
        ]

        if self.finished:
            return

        # resolve speed safely

        player_speed = max(0.1, self.player.attack_speed)
        enemy_speed = max(0.1, self.enemy.attack_speed)

        player_delay = 1000 / player_speed
        enemy_delay = 1000 / enemy_speed

        # PLAYER TURN
        if now - self.player_last_attack >= player_delay:
            if self.player.is_alive() and self.enemy.is_alive():
                self._add_combat_events(self.combat.hit(self.player, self.enemy))
            self.player_last_attack = now

        # ENEMY TURN
        if now - self.enemy_last_attack >= enemy_delay:
            if self.enemy.is_alive() and self.player.is_alive():
                self._add_combat_events(self.combat.hit(self.enemy, self.player))
            self.enemy_last_attack = now

        # PASSIVE TICKS
        dt = 1 / 60

        for unit in (self.player, self.enemy):
            if not unit.is_alive():
                continue
            for p in unit.passives:
                p.on_tick(unit, dt)

        # END CONDITION
        if not self.player.is_alive() or not self.enemy.is_alive():
            self.finished = True
            self.winner = "player" if self.player.is_alive() else "enemy"

            for unit in (self.player, self.enemy):
                for p in unit.passives:
                    p.on_combat_end(unit)

    # --------------------------------------------------------
    # DRAW (unchanged, just stabilized)
    # --------------------------------------------------------

    def draw(self, screen):
        width, height = screen.get_size()
        scale = ui_scale(screen)
        player_size = max(48, round(120 * scale * getattr(self.player, "size", 1.0)))
        enemy_size = max(48, round(120 * scale * getattr(self.enemy, "size", 1.0)))
        y = round(height * 0.38)
        player_x = round(width * 0.28 - player_size / 2)
        enemy_x = round(width * 0.72 - enemy_size / 2)
        self.draw_character(screen, self.player, player_x, y, player_size)
        self.draw_character(screen, self.enemy, enemy_x, y, enemy_size)

        now = pygame.time.get_ticks()
        anchors = {
            self.player: (player_x + player_size // 2, y + round(8 * scale)),
            self.enemy: (enemy_x + enemy_size // 2, y + round(8 * scale)),
        }
        for item in self.combat_texts:
            item.draw(screen, anchors[item.character], scale, now)

    def _add_combat_events(self, events):
        for event in events:
            kind = event["kind"]
            amount = event.get("amount")
            if amount is None:
                label = "DODGED!"
            else:
                value = f"{amount:.1f}" if 0 < amount < 1 else str(round(amount))
                labels = {
                    "damage": f"-{value}",
                    "critical": f"CRITICAL! -{value}",
                    "block": f"BLOCKED {value}",
                    "heal": f"+{value} HP",
                }
                label = labels[kind]
            character = event["character"]
            occupied_lanes = {
                item.lane for item in self.combat_texts
                if item.character is character
            }
            lane = 0
            if lane in occupied_lanes:
                magnitude = 1
                while True:
                    candidates = (-magnitude, magnitude)
                    lane = next((candidate for candidate in candidates if candidate not in occupied_lanes), None)
                    if lane is not None:
                        break
                    magnitude += 1
            self.combat_texts.append(FloatingCombatText(character, kind, label, lane))

    def draw_character(self, screen, char, x, y, size):

        offset = 0
        if char.is_alive():
            offset = (pygame.time.get_ticks() // 200) % 4

        y -= offset

        if char.sprite_name:
            try:
                img = get_sprite(char.sprite_name, (size, size))
                screen.blit(img, (x, y))
            except Exception as e:
                print("SPRITE ERROR:", char.sprite_name, e)
                pygame.draw.rect(screen, char.color, (x, y, size, size))
        else:
            pygame.draw.rect(screen, char.color, (x, y, size, size))

        # HP BAR
        hp_ratio = max(0, char.hp / char.max_hp)
        bar_height = max(3, round(5 * ui_scale(screen)))
        bar_y = y - round(10 * ui_scale(screen))

        pygame.draw.rect(screen, (200, 0, 0), (x, bar_y, size, bar_height))
        pygame.draw.rect(screen, (0, 200, 0), (x, bar_y, size * hp_ratio, bar_height))

import pygame
import random

from ui.draw import get_sprite


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
            return

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
            return  # attack missed

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

        # -------------------------
        # 6. ARMOR REDUCTION
        # -------------------------
        dmg = max(0, dmg - def_stats["armor"] * 0.3)

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
        attacker.hp = min(attacker.max_hp, attacker.hp + heal)

        # -------------------------
        # 10. DEATH CHECK (FIXED)
        # -------------------------
        if target.hp <= 0:
            target.hp = 0


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

        self.player_last_attack = 0
        self.enemy_last_attack = 0

        # combat start hooks
        for unit in (self.player, self.enemy):
            for p in unit.passives:
                p.on_combat_start(unit)

    # --------------------------------------------------------

    def update(self):

        if self.finished:
            return

        now = pygame.time.get_ticks()

        # resolve speed safely
        p_stats = self.combat.resolve_attack_stats(self.player)
        e_stats = self.combat.resolve_attack_stats(self.enemy)

        player_speed = max(0.1, p_stats["speed"])
        enemy_speed = max(0.1, e_stats["speed"])

        player_delay = 1000 / player_speed
        enemy_delay = 1000 / enemy_speed

        # PLAYER TURN
        if now - self.player_last_attack >= player_delay:
            if self.player.is_alive() and self.enemy.is_alive():
                self.combat.hit(self.player, self.enemy)
            self.player_last_attack = now

        # ENEMY TURN
        if now - self.enemy_last_attack >= enemy_delay:
            if self.enemy.is_alive() and self.player.is_alive():
                self.combat.hit(self.enemy, self.player)
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
        self.draw_character(screen, self.player)
        self.draw_character(screen, self.enemy)

    def draw_character(self, screen, char):

        offset = 0
        if char.is_alive():
            offset = (pygame.time.get_ticks() // 200) % 4

        y = char.y - offset

        if char.sprite_name:
            try:
                img = get_sprite(char.sprite_name)
                screen.blit(img, (char.x, y))
            except Exception as e:
                print("SPRITE ERROR:", char.sprite_name, e)
                pygame.draw.rect(screen, char.color, (char.x, char.y, 80, 80))
        else:
            pygame.draw.rect(screen, char.color, (char.x, char.y, 80, 80))

        # HP BAR
        hp_ratio = max(0, char.hp / char.max_hp)

        pygame.draw.rect(screen, (200, 0, 0), (char.x, char.y - 10, 80, 5))
        pygame.draw.rect(screen, (0, 200, 0), (char.x, char.y - 10, 80 * hp_ratio, 5))
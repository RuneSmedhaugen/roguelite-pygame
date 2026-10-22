import pygame
import random
import math

from ui.draw import get_sprite
from ui.layout import font, scaled, ui_scale
from ui.combat_text import FloatingCombatText
from ui.combat_effects import CombatEffects
from core.combat import CombatEngine

ATTACK_HIT_SOUNDS = (
    "soundscrate-fighting-impact-punch.mp3",
    "soundscrate-fighting-punch-1.mp3",
    "soundscrate-fighting-punch-2.mp3",
    "soundscrate-fighting-punch-3.mp3",
)
DODGE_SOUND = "dodge.wav"


class Battle:

    def __init__(self, player, enemy, sound_effects=None):
        self.player = player
        self.enemy = enemy
        self.sound_effects = sound_effects

        self.finished = False
        self.winner = None

        self.combat = CombatEngine()
        self.combat_texts = []
        self.attack_animations = {}
        self.reactions = {}
        self.pending_visual_events = []
        self.effects = CombatEffects()

        self.player_last_attack = 0
        self.enemy_last_attack = 0
        self.last_update_at = pygame.time.get_ticks()

        # combat start hooks
        for unit in (self.player, self.enemy):
            unit.status_effects.clear()
            for p in unit.passives:
                p.on_combat_start(unit)

    # --------------------------------------------------------

    def update(self):

        now = pygame.time.get_ticks()
        dt = min(0.1, max(0.0, (now - self.last_update_at) / 1000))
        self.last_update_at = now
        self.combat_texts = [
            item for item in self.combat_texts
            if now - item.created_at < item.duration
        ]

        if self.finished:
            return

        # resolve speed safely

        player_speed = self.combat.resolve_attack_speed(self.player)
        enemy_speed = self.combat.resolve_attack_speed(self.enemy)

        player_delay = 1000 / player_speed
        enemy_delay = 1000 / enemy_speed

        # PLAYER TURN
        if now - self.player_last_attack >= player_delay:
            if self.player.is_alive() and self.enemy.is_alive():
                events = self.combat.hit(self.player, self.enemy)
                if self.sound_effects:
                    sound = DODGE_SOUND if any(event["kind"] == "dodge" for event in events) else random.choice(ATTACK_HIT_SOUNDS)
                    self.sound_effects.play(sound)
                self._add_combat_events(events)
                self._start_visual_attack(self.player, events, now)
            self.player_last_attack = now

        # ENEMY TURN
        if now - self.enemy_last_attack >= enemy_delay:
            if self.enemy.is_alive() and self.player.is_alive():
                events = self.combat.hit(self.enemy, self.player)
                if self.sound_effects:
                    sound = DODGE_SOUND if any(event["kind"] == "dodge" for event in events) else random.choice(ATTACK_HIT_SOUNDS)
                    self.sound_effects.play(sound)
                self._add_combat_events(events)
                self._start_visual_attack(self.enemy, events, now)
            self.enemy_last_attack = now

        # PASSIVE TICKS
        for unit in (self.player, self.enemy):
            if not unit.is_alive():
                continue
            for p in unit.passives:
                p.on_tick(unit, dt)
        self._add_combat_events(self.combat._passive_events((self.player, self.enemy)))

        for unit in (self.player, self.enemy):
            self._add_combat_events(unit.update_status_effects(dt))

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

    def draw(self, screen, animation_time=None):
        now = pygame.time.get_ticks() if animation_time is None else animation_time
        width, height = screen.get_size()
        scale = ui_scale(screen)
        player_size = max(48, round(120 * scale * getattr(self.player, "size", 1.0)))
        enemy_size = max(48, round(120 * scale * getattr(self.enemy, "size", 1.0)))
        ground_y = round(height * 0.745)
        player_y = ground_y - player_size
        enemy_y = ground_y - enemy_size
        player_x = round(width * 0.37 - player_size / 2)
        enemy_x = round(width * 0.63 - enemy_size / 2)
        player_pose = self._pose(self.player, player_x, player_y, player_size, now, scale)
        enemy_pose = self._pose(self.enemy, enemy_x, enemy_y, enemy_size, now, scale)
        self.draw_character(screen, self.player, player_pose[0], player_pose[1], player_size, player_pose[2])
        self.draw_character(screen, self.enemy, enemy_pose[0], enemy_pose[1], enemy_size, enemy_pose[2])

        anchors = {
            self.player: (player_pose[0] + player_size // 2, player_pose[1] + round(8 * scale)),
            self.enemy: (enemy_pose[0] + enemy_size // 2, enemy_pose[1] + round(8 * scale)),
        }

        base_positions = {
            self.player: (player_x, player_y, player_size),
            self.enemy: (enemy_x, enemy_y, enemy_size),
        }
        for event, attacker, event_time in self.pending_visual_events:
            target = event["character"]
            target_x, target_y, target_size = base_positions[target]
            kind = event["kind"]
            if kind == "dodge":
                impact = (target_x + target_size // 2, target_y + round(target_size * 0.88))
            elif kind == "heal":
                impact = (target_x + target_size // 2, target_y + round(target_size * 0.42))
            else:
                direction = 1 if attacker is self.player else -1
                impact = (
                    target_x + target_size // 2 - direction * round(target_size * 0.28),
                    target_y + round(target_size * 0.52),
                )
            self.effects.burst(impact, kind, event_time, scale)
        self.pending_visual_events.clear()
        self.effects.draw(screen, now)
        for item in self.combat_texts:
            item.draw(screen, anchors[item.character], scale, now)

    def draw_intro(self, screen, speaker, progress, animation_time=None):
        """Show each fighter speaking in turn before combat begins."""
        now = pygame.time.get_ticks() if animation_time is None else animation_time
        width, height = screen.get_size()
        scale = ui_scale(screen)
        ground_y = round(height * 0.745)
        midpoint = width // 2

        for character, side in ((self.player, "left"), (self.enemy, "right")):
            base_size = max(48, round(120 * scale * getattr(character, "size", 1.0)))
            center_x = round(width * (0.37 if side == "left" else 0.63))
            speaking = character is speaker
            if speaking:
                swell = math.sin(math.pi * max(0.0, min(1.0, progress)))
                shake = math.sin(progress * math.tau * 5) * scaled(screen, 6) * swell
                size = round(base_size * (1 + 0.17 * swell))
                y_bob = -round(scaled(screen, 6) * swell)
                center_x += round(shake)
            else:
                size = base_size
                y_bob = round(math.sin(now / 260 + (0 if side == "left" else math.pi)) * scaled(screen, 2))

            x = center_x - size // 2
            y = ground_y - size + y_bob
            self.draw_character(screen, character, x, y, size)

            if speaking:
                label = font(screen, 30, bold=True).render(f"{character.name}!", True, (255, 229, 158))
                label_rect = label.get_rect(center=(center_x, y - scaled(screen, 24)))
                shadow = font(screen, 30, bold=True).render(f"{character.name}!", True, (22, 21, 28))
                screen.blit(shadow, shadow.get_rect(center=(label_rect.centerx, label_rect.centery + scaled(screen, 2))))
                screen.blit(label, label_rect)

        pygame.draw.line(screen, (88, 79, 72), (midpoint, round(height * 0.57)), (midpoint, height), max(1, scaled(screen, 2)))

    def draw_outcome(self, screen, winner, progress):
        width, height = screen.get_size()
        scale = ui_scale(screen)
        midpoint = width // 2
        winner_is_player = winner == "player"
        winner_rect = pygame.Rect(0 if winner_is_player else midpoint, 0, midpoint if winner_is_player else width - midpoint, height)
        loser_rect = pygame.Rect(midpoint if winner_is_player else 0, 0, width - midpoint if winner_is_player else midpoint, height)

        winner_tint = pygame.Surface(winner_rect.size, pygame.SRCALPHA)
        winner_tint.fill((255, 232, 142, 36))
        screen.blit(winner_tint, winner_rect)
        loser_tint = pygame.Surface(loser_rect.size, pygame.SRCALPHA)
        loser_tint.fill((105, 114, 128, 112))
        screen.blit(loser_tint, loser_rect)
        pygame.draw.line(screen, (206, 205, 186), (midpoint, 0), (midpoint, height), max(1, scaled(screen, 2)))

        player_size = max(48, round(120 * scale * getattr(self.player, "size", 1.0)))
        enemy_size = max(48, round(120 * scale * getattr(self.enemy, "size", 1.0)))
        ground_y = round(height * 0.745)
        layouts = (
            (self.player, round(width * 0.37 - player_size / 2), ground_y - player_size, player_size, winner_is_player),
            (self.enemy, round(width * 0.63 - enemy_size / 2), ground_y - enemy_size, enemy_size, not winner_is_player),
        )

        fall_progress = min(1.0, progress / 0.62)
        fall_progress = fall_progress * fall_progress * (3 - 2 * fall_progress)
        for character, x, y, size, is_winner in layouts:
            if not character.sprite_name:
                continue
            image = get_sprite(
                character.sprite_name,
                (size, size),
                flip_x=character is self.enemy,
            )
            if is_winner:
                bounce = abs(math.sin(progress * math.tau * 2)) * 30 * scale
                image = image.copy()
                image.fill((30, 22, 0), special_flags=pygame.BLEND_RGB_ADD)
                center = (x + size // 2, round(y + size / 2 - bounce))
                angle = 0
            else:
                image = pygame.transform.grayscale(image)
                fall_direction = 1 if x < midpoint else -1
                center = (x + size // 2, round(y + size / 2 + fall_progress * 40 * scale))
                angle = round(-fall_direction * 78 * fall_progress)
                image = pygame.transform.rotate(image, angle)
            screen.blit(image, image.get_rect(center=center))

        confetti_colors = (
            (255, 211, 75), (255, 105, 91), (93, 220, 163),
            (106, 193, 255), (255, 238, 183), (210, 137, 255),
        )
        for index in range(34):
            cycle = (progress * 1.35 + index * 0.137) % 1.0
            x_range = max(1, winner_rect.width - scaled(screen, 24))
            x = winner_rect.left + scaled(screen, 12) + ((index * 47 + round(progress * 23)) % x_range)
            y = round(height * (0.08 + cycle * 0.64))
            size = scaled(screen, 4 + index % 4)
            color = confetti_colors[index % len(confetti_colors)]
            pygame.draw.rect(screen, color, (x, y, size, max(2, size // 2)))

    def _start_visual_attack(self, attacker, events, now):
        direction = 1 if attacker is self.player else -1
        self.attack_animations[attacker] = {"start": now, "direction": direction}

        priorities = {"block": 1, "damage": 2, "critical": 3, "dodge": 3}
        reaction = None
        target = self.enemy if attacker is self.player else self.player
        for event in events:
            self.pending_visual_events.append((event, attacker, now))
            if event["character"] is target and event["kind"] in priorities:
                if reaction is None or priorities[event["kind"]] > priorities[reaction]:
                    reaction = event["kind"]

        if reaction is not None:
            self.reactions[target] = {
                "kind": reaction,
                "start": now,
                "direction": direction,
            }

    def _pose(self, character, x, y, size, now, scale):
        offset_x = 0.0
        offset_y = math.sin(now / 260 + (0 if character is self.player else math.pi)) * 2.2 * scale
        flash = None
        attack = self.attack_animations.get(character)
        if attack is not None:
            progress = (now - attack["start"]) / 360
            if progress >= 1:
                self.attack_animations.pop(character, None)
            else:
                outbound_end, hold_end = 0.34, 0.49
                if progress < outbound_end:
                    phase = progress / outbound_end
                    lunge = phase * phase * (3 - 2 * phase)
                elif progress < hold_end:
                    lunge = 1.0
                else:
                    phase = (progress - hold_end) / (1 - hold_end)
                    lunge = 1 - phase * phase * (3 - 2 * phase)
                offset_x += attack["direction"] * 30 * scale * lunge

        reaction = self.reactions.get(character)
        if reaction is not None:
            duration = 320 if reaction["kind"] == "dodge" else 260
            progress = (now - reaction["start"]) / duration
            if progress >= 1:
                self.reactions.pop(character, None)
            else:
                wave = math.sin(math.pi * max(0.0, progress))
                direction = reaction["direction"]
                if reaction["kind"] == "dodge":
                    offset_x += direction * 20 * scale * wave
                    offset_y -= 16 * scale * wave
                elif reaction["kind"] == "block":
                    offset_x += direction * 5 * scale * wave
                    flash = ((100, 205, 255), round(190 * max(0, 1 - progress / 0.68)))
                else:
                    force = 17 if reaction["kind"] == "critical" else 10
                    offset_x += direction * force * scale * wave
                    offset_y -= 4 * scale * wave
                    color = (255, 203, 76) if reaction["kind"] == "critical" else (255, 255, 255)
                    flash = (color, round(210 * max(0, 1 - progress / 0.55)))

        return round(x + offset_x), round(y + offset_y), flash

    def _add_combat_events(self, events):
        for event in events:
            kind = event["kind"]
            amount = event.get("amount")
            if kind == "passive":
                label = event.get("label", "PASSIVE!")
            elif amount is None:
                label = "DODGED!"
            else:
                value = f"{amount:.1f}" if 0 < amount < 1 else str(round(amount))
                labels = {
                    "damage": f"-{value}",
                    "critical": f"CRITICAL! -{value}",
                    "block": f"BLOCKED {value}",
                    "heal": f"+{value} HP",
                }
                label = event.get("label", labels[kind])
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

    def draw_character(self, screen, char, x, y, size, flash=None):
        if char.sprite_name:
            try:
                img = get_sprite(
                    char.sprite_name,
                    (size, size),
                    flip_x=char is self.enemy,
                )
                if flash is not None and flash[1] > 0:
                    img = img.copy()
                    tint = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                    tint.fill((*flash[0], flash[1]))
                    img.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
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

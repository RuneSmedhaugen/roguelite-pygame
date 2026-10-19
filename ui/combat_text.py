"""Short-lived, resolution-aware combat callouts."""

import math

import pygame

class FloatingCombatText:
    DURATIONS = {
        "damage": 700,
        "critical": 950,
        "dodge": 700,
        "block": 700,
        "heal": 700,
        "passive": 900,
    }
    COLORS = {
        "damage": (255, 105, 82),
        "critical": (255, 205, 55),
        "dodge": (255, 85, 105),
        "block": (125, 205, 255),
        "heal": (105, 255, 145),
        "passive": (255, 226, 112),
    }

    def __init__(self, character, kind, text, lane=0):
        self.character = character
        self.kind = kind
        self.text = text
        self.lane = lane
        self.created_at = pygame.time.get_ticks()
        self.duration = self.DURATIONS[kind]

    def draw(self, screen, anchor, scale, now):
        progress = min(1.0, (now - self.created_at) / self.duration)
        alpha = round(255 * (1 - progress) ** 1.35)

        # Separate event types by direction, then offset each active callout
        # perpendicular to its path so rapid events have distinct lanes.
        directions = {
            "damage": (0.0, -1.0),
            "critical": (0.0, -1.0),
            "dodge": (-0.68, -0.73),
            "block": (-0.68, -0.73),
            "heal": (0.68, -0.73),
            "passive": (0.0, -1.0),
        }
        dx, dy = directions[self.kind]
        perpendicular = (-dy, dx)
        travel = progress * 62 * scale
        lane_offset = self.lane * 68 * scale
        x = anchor[0] + dx * travel + perpendicular[0] * lane_offset
        y = anchor[1] + dy * travel + perpendicular[1] * lane_offset - 12 * scale

        critical = self.kind == "critical"
        base_size = 31 if critical else 25
        pulse = 1 + (0.13 * math.sin(progress * math.pi * 5) if critical else 0)
        font = pygame.font.SysFont(None, max(1, round(base_size * scale * pulse)), bold=True)
        image = font.render(self.text, True, self.COLORS[self.kind])
        image.set_alpha(alpha)
        outline = font.render(self.text, True, (20, 12, 20))
        outline.set_alpha(alpha)
        rect = image.get_rect(center=(round(x), round(y)))

        # A dark outline keeps the callout readable over bright sprites and effects.
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            screen.blit(outline, rect.move(round(dx * scale), round(dy * scale)))
        screen.blit(image, rect)

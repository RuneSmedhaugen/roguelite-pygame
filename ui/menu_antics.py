"""Small, looping character cameos for the main menu."""

import math
import random

import pygame

from core.characters import CHARACTERS
from ui.draw import get_sprite
from ui.layout import ui_scale


class MenuAntics:
    RAINBOW = (
        (255, 72, 82),
        (255, 151, 65),
        (255, 222, 75),
        (85, 220, 128),
        (79, 167, 255),
        (183, 112, 255),
    )

    def __init__(self):
        self.rng = random.Random()
        self.sprites = [
            character["sprite"]
            for character in CHARACTERS
            if character.get("sprite")
        ]
        self.sprite_bag = []
        self.last_sprite_by_role = {}
        self.screen_size = None
        self.last_update = None
        self.bouncers = []
        self.hoppers = []
        self.peekers = []
        self.zoomers = []

    def _next_sprite(self, role):
        """Cycle through the roster before repeating, changing each role on renewal."""
        if not self.sprites:
            return None

        if not self.sprite_bag:
            self.sprite_bag = self.sprites[:]
            self.rng.shuffle(self.sprite_bag)

        previous = self.last_sprite_by_role.get(role)
        if len(self.sprite_bag) > 1 and self.sprite_bag[-1] == previous:
            self.sprite_bag[0], self.sprite_bag[-1] = self.sprite_bag[-1], self.sprite_bag[0]
        sprite = self.sprite_bag.pop()
        self.last_sprite_by_role[role] = sprite
        return sprite

    def _reset_positions(self, screen, now, base_size):
        width, height = screen.get_size()
        self.screen_size = (width, height)

        # Several small characters are always moving around the menu.
        self.bouncers = []
        for index in range(2):
            size = round(base_size * self.rng.uniform(0.78, 1.0))
            self.bouncers.append({
                "sprite": self._next_sprite(f"bounce-{index}"),
                "size": size,
                "x": self.rng.uniform(0, max(0, width - size)),
                "y": self.rng.uniform(height * 0.12, max(height * 0.12, height - size)),
                "vx": self.rng.choice((-1, 1)) * self.rng.uniform(90, 155),
                "vy": self.rng.choice((-1, 1)) * self.rng.uniform(75, 125),
            })

        self.hoppers = []
        for index in range(1):
            size = round(base_size * self.rng.uniform(0.8, 1.05))
            x = self.rng.uniform(0, max(0, width - size))
            y = self.rng.uniform(height * 0.2, max(height * 0.2, height - size))
            actor = {
                "sprite": self._next_sprite(f"hop-{index}"),
                "size": size,
                "x": x,
                "y": y,
                "from_x": x,
                "from_y": y,
                "to_x": x,
                "to_y": y,
                "started": now,
                "duration": self.rng.randint(900, 1500),
            }
            self._choose_hop_target(actor, width, height, now)
            self.hoppers.append(actor)

        self.peekers = []
        for index in range(2):
            self.peekers.append({
                "sprite": self._next_sprite(f"peek-{index}"),
                "started": now - self.rng.randint(0, 900),
                "next_at": now + self.rng.randint(500, 2100),
                "edge": self.rng.choice(("top", "left", "right")),
                "position": self.rng.random(),
            })

        self.zoomers = [{
            "sprite": self._next_sprite("zoom"),
            "active": False,
            "next_at": now + self.rng.randint(700, 1500),
            "x": 0,
            "y": 0,
            "speed": 0,
        }]

    def _choose_hop_target(self, actor, width, height, now):
        actor["from_x"] = actor["x"]
        actor["from_y"] = actor["y"]
        actor["to_x"] = self.rng.uniform(0, max(0, width - actor["size"]))
        actor["to_y"] = self.rng.uniform(
            height * 0.15, max(height * 0.15, height - actor["size"])
        )
        actor["started"] = now
        actor["duration"] = self.rng.randint(900, 1500)

    def draw(self, screen, now):
        width, height = screen.get_size()
        scale = min(ui_scale(screen), 1.35)
        base_size = max(26, round(43 * scale))
        if self.screen_size != (width, height):
            self._reset_positions(screen, now, base_size)

        dt = 0 if self.last_update is None else min(
            0.05, max(0, (now - self.last_update) / 1000)
        )
        self.last_update = now

        # Ricocheting characters change identity at each wall bounce.
        for index, actor in enumerate(self.bouncers):
            size = actor["size"]
            actor["x"] += actor["vx"] * dt
            actor["y"] += actor["vy"] * dt
            bounced = False
            if actor["x"] < 0 or actor["x"] + size > width:
                actor["vx"] *= -1
                actor["x"] = max(0, min(width - size, actor["x"]))
                bounced = True
            if actor["y"] < 0 or actor["y"] + size > height:
                actor["vy"] *= -1
                actor["y"] = max(0, min(height - size, actor["y"]))
                bounced = True
            if bounced:
                actor["sprite"] = self._next_sprite(f"bounce-{index}")
            self._draw_sprite(screen, actor["sprite"], size, actor["x"], actor["y"])

        # Hoppers switch to a new character whenever they land.
        for index, actor in enumerate(self.hoppers):
            if now - actor["started"] >= actor["duration"]:
                actor["x"], actor["y"] = actor["to_x"], actor["to_y"]
                actor["sprite"] = self._next_sprite(f"hop-{index}")
                self._choose_hop_target(actor, width, height, now)
            progress = min(1, (now - actor["started"]) / actor["duration"])
            eased = progress * progress * (3 - 2 * progress)
            hop_x = actor["from_x"] + (actor["to_x"] - actor["from_x"]) * eased
            hop_y = actor["from_y"] + (actor["to_y"] - actor["from_y"]) * eased
            hop_y -= math.sin(math.pi * progress) * actor["size"] * 0.55
            self._draw_sprite(screen, actor["sprite"], actor["size"], hop_x, hop_y)

        # Two independent peekers pop in from different edges on their own timers.
        for index, actor in enumerate(self.peekers):
            if now >= actor["next_at"]:
                actor["sprite"] = self._next_sprite(f"peek-{index}")
                actor["edge"] = self.rng.choice(("top", "left", "right"))
                actor["position"] = self.rng.random()
                actor["started"] = now
                actor["next_at"] = now + self.rng.randint(2300, 3700)
            phase = now - actor["started"]
            if phase < 850:
                if actor["edge"] == "top":
                    x, y = actor["position"] * max(0, width - base_size), -base_size * 0.25
                elif actor["edge"] == "left":
                    x, y = -base_size * 0.25, actor["position"] * max(0, height - base_size)
                else:
                    x, y = width - base_size * 0.75, actor["position"] * max(0, height - base_size)
                pop = min(1, max(0, phase / 170))
                self._draw_sprite(screen, actor["sprite"], base_size * (0.5 + 0.5 * pop), x, y)

        # The rainbow flyby also gets a fresh member of the cast each pass.
        for actor in self.zoomers:
            if not actor["active"] and now >= actor["next_at"]:
                actor["active"] = True
                actor["sprite"] = self._next_sprite("zoom")
                actor["x"] = -base_size
                actor["y"] = self.rng.uniform(height * 0.16, height * 0.84)
                actor["speed"] = width / self.rng.uniform(1.0, 1.7)
            if actor["active"]:
                actor["x"] += actor["speed"] * dt
                stripe_height = max(2, round(base_size / 7))
                trail_width = round(base_size * 2.3)
                for index, color in enumerate(self.RAINBOW):
                    rect = pygame.Rect(
                        round(actor["x"] - trail_width),
                        round(actor["y"] + index * stripe_height),
                        trail_width,
                        stripe_height + 1,
                    )
                    pygame.draw.rect(screen, color, rect)
                self._draw_sprite(screen, actor["sprite"], base_size, actor["x"], actor["y"])
                if actor["x"] > width + base_size:
                    actor["active"] = False
                    actor["next_at"] = now + self.rng.randint(1000, 2300)

    @staticmethod
    def _draw_sprite(screen, sprite_name, size, x, y):
        if not sprite_name:
            return
        size = max(1, round(size))
        image = get_sprite(sprite_name, (size, size))
        screen.blit(image, (round(x), round(y)))

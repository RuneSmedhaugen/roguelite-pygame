"""Procedural impact particles and rings for combat feedback."""

import math

import pygame


class CombatEffects:
    PALETTES = {
        "damage": ((255, 132, 72), (255, 222, 157)),
        "critical": ((255, 184, 43), (255, 247, 179)),
        "block": ((76, 190, 255), (207, 244, 255)),
        "dodge": ((118, 198, 226), (222, 248, 255)),
        "heal": ((74, 225, 128), (208, 255, 218)),
        "passive": ((255, 190, 59), (255, 244, 166)),
    }

    def __init__(self):
        self.particles = []
        self.rings = []

    def burst(self, position, kind, now, scale):
        outer_color, inner_color = self.PALETTES[kind]
        count = {"damage": 8, "critical": 14, "block": 8, "dodge": 7, "heal": 6, "passive": 5}[kind]
        duration = 390 if kind == "critical" else 310
        for index in range(count):
            angle = (math.tau * index / count) - math.pi / 2
            speed = (72 + (index % 3) * 22) * scale
            self.particles.append({
                "x": float(position[0]),
                "y": float(position[1]),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 24 * scale,
                "born": now,
                "duration": duration + (index % 2) * 45,
                "size": (2.0 + (index % 3) * 0.55) * scale,
                "color": inner_color if index % 3 == 0 else outer_color,
            })

        if kind in ("damage", "critical", "block"):
            self.rings.append({
                "x": float(position[0]),
                "y": float(position[1]),
                "born": now,
                "duration": 270 if kind != "critical" else 360,
                "color": outer_color,
                "scale": scale,
                "max_radius": 24 if kind != "critical" else 38,
            })

    def draw(self, screen, now):
        active_particles = []
        for particle in self.particles:
            progress = (now - particle["born"]) / particle["duration"]
            if progress >= 1:
                continue
            active_particles.append(particle)
            seconds = max(0, now - particle["born"]) / 1000
            x = particle["x"] + particle["vx"] * seconds
            y = particle["y"] + particle["vy"] * seconds + 125 * seconds * seconds
            fade = max(0.0, 1 - progress)
            color = tuple(round(channel * fade) for channel in particle["color"])
            radius = max(1, round(particle["size"] * (0.55 + fade * 0.45)))
            tail_x = x - particle["vx"] * 0.035
            tail_y = y - particle["vy"] * 0.035
            pygame.draw.line(screen, color, (round(tail_x), round(tail_y)), (round(x), round(y)), radius)
            pygame.draw.circle(screen, color, (round(x), round(y)), radius)
        self.particles = active_particles

        active_rings = []
        for ring in self.rings:
            progress = (now - ring["born"]) / ring["duration"]
            if progress >= 1:
                continue
            active_rings.append(ring)
            fade = max(0.0, 1 - progress)
            color = tuple(round(channel * fade) for channel in ring["color"])
            radius = max(2, round((5 + ring["max_radius"] * progress) * ring["scale"]))
            pygame.draw.circle(
                screen,
                color,
                (round(ring["x"]), round(ring["y"])),
                radius,
                width=max(1, round(2 * ring["scale"])),
            )
        self.rings = active_rings

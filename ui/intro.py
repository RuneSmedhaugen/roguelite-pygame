"""A short, non-skippable mascot and title reveal shown before asset loading."""

import math
import random

import pygame


INTRO_DURATION_MS = 5000
INTRO_SCREAM = "Loud-male-scream-sound-effect.mp3"
GLASS_BREAK_SOUND = "soundscrate-dropped-glass-1.mp3"
HAMMY_LUNGE_START_MS = 700
HAMMY_LUNGE_DURATION_MS = 2000
HAMMY_LUNGE_PEAK_MS = HAMMY_LUNGE_START_MS + HAMMY_LUNGE_DURATION_MS // 2
PUNCH_IMPACT_MS = INTRO_DURATION_MS // 2
GLASS_SOUND_EARLY_MS = 300


def _make_backdrop(size):
    width, height = size
    surface = pygame.Surface(size)
    top = (7, 8, 16)
    bottom = (27, 10, 18)
    for y in range(height):
        amount = y / max(1, height - 1)
        color = tuple(round(a + (b - a) * amount) for a, b in zip(top, bottom))
        pygame.draw.line(surface, color, (0, y), (width, y))

    glow = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (105, 25, 35, 48),
                        (round(width * .18), round(height * .04),
                         round(width * .64), round(height * .80)))
    surface.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    vignette = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(vignette, (0, 0, 0, 95), vignette.get_rect(),
                     border_radius=max(1, round(min(size) * .12)),
                     width=max(1, round(min(size) * .035)))
    surface.blit(vignette, (0, 0))
    return surface


def _crack_burst(surface, center, radius_x, radius_y, progress):
    """Draw a brief glass-impact motif contained around the PUNCH word."""
    if progress <= 0 or progress >= 1:
        return
    alpha = round(225 * min(1.0, (1.0 - progress) * 3.0))
    cx, cy = center
    points = []
    for index in range(12):
        angle = (index / 12) * math.tau + .12
        distance = 0.68 + .24 * ((index * 7) % 5) / 4
        points.append((round(cx + math.cos(angle) * radius_x * distance),
                       round(cy + math.sin(angle) * radius_y * distance)))
    for index, point in enumerate(points):
        next_point = points[(index + 1) % len(points)]
        pygame.draw.line(surface, (235, 196, 157, alpha), center, point, 2)
        pygame.draw.line(surface, (115, 151, 181, alpha // 2), point, next_point, 1)

    for index in range(7):
        angle = index * (math.tau / 7) + .31
        distance = 1.05 + progress * .48
        x = cx + math.cos(angle) * radius_x * distance
        y = cy + math.sin(angle) * radius_y * distance
        length_x = radius_x * .10
        length_y = radius_y * .10
        tip = (round(x + math.cos(angle) * length_x), round(y + math.sin(angle) * length_y))
        side = (round(x + math.cos(angle + 1.3) * length_x * .45),
                round(y + math.sin(angle + 1.3) * length_y * .45))
        pygame.draw.polygon(surface, (170, 208, 225, alpha // 2),
                            [(round(x), round(y)), tip, side])


def _outlined_text(font, text, color, outline_color, thickness):
    """Give the title a clean, high-contrast edge on any background."""
    glyphs = font.render(text, True, color)
    outline = font.render(text, True, outline_color)
    padding = max(1, thickness)
    result = pygame.Surface(
        (glyphs.get_width() + padding * 2, glyphs.get_height() + padding * 2),
        pygame.SRCALPHA,
    )
    radius_squared = padding * padding
    for offset_y in range(-padding, padding + 1):
        for offset_x in range(-padding, padding + 1):
            if offset_x * offset_x + offset_y * offset_y <= radius_squared:
                result.blit(outline, (padding + offset_x, padding + offset_y))
    result.blit(glyphs, (padding, padding))
    return result


def play_startup_intro(screen, mascot, clock, sound_effects):
    """Play the opening reveal, ignoring input so it cannot be accidentally skipped."""
    size = screen.get_size()
    width, height = size
    backdrop = _make_backdrop(size)
    mascot_size = max(1, round(min(width * .43, height * .56)))
    image = pygame.transform.smoothscale(mascot, (mascot_size, mascot_size))
    image.fill((198, 187, 196, 255), special_flags=pygame.BLEND_RGBA_MULT)
    shadow = pygame.transform.smoothscale(
        image, (round(mascot_size * 1.035), round(mascot_size * 1.035)))
    shadow.fill((18, 4, 9, 180), special_flags=pygame.BLEND_RGBA_MULT)
    # Prepare a few lunge sizes up front so the two-second motion stays smooth.
    lunge_images = []
    lunge_shadows = []
    for frame in range(9):
        scale = 1.0 + .18 * frame / 8
        frame_size = (round(mascot_size * scale), round(mascot_size * scale))
        lunge_images.append(pygame.transform.smoothscale(image, frame_size))
        lunge_shadows.append(pygame.transform.smoothscale(shadow, (
            round(shadow.get_width() * scale), round(shadow.get_height() * scale))))

    # Arial/Segoe style sans faces stay readable across Windows and fall back
    # cleanly to the system sans-serif on machines with other font sets.
    small_font = pygame.font.SysFont("arial", max(26, round(height * .060)), bold=True)
    punch_font = pygame.font.SysFont("arial", max(38, round(height * .108)), bold=True)
    puppies_font = pygame.font.SysFont("arial", max(32, round(height * .088)), bold=True)
    title_fonts = {"SMALL": small_font, "PUNCH": punch_font, "PUPPIES": puppies_font}
    title_colors = {
        "SMALL": (224, 220, 208),
        "PUNCH": (255, 194, 105),
        "PUPPIES": (237, 232, 220),
    }
    outline_width = max(2, round(height * .006))
    words = {
        key: _outlined_text(title_fonts[key], key, color, (38, 18, 22), outline_width)
        for key, color in title_colors.items()
    }
    shadow_words = {
        key: _outlined_text(title_fonts[key], key, (12, 8, 13), (12, 8, 13), outline_width)
        for key in words
    }
    onsets = {"SMALL": .28, "PUNCH": .43, "PUPPIES": .61}
    start = pygame.time.get_ticks()
    scream_channel = None
    scream_started_at = None
    scream_duration_ms = None
    glass_break_played = False
    sparks = [(random.random(), random.random(), random.random() * 2.0) for _ in range(22)]

    while True:
        now = pygame.time.get_ticks()
        elapsed = now - start
        progress = min(1.0, elapsed / INTRO_DURATION_MS)
        if scream_channel is None and elapsed >= HAMMY_LUNGE_PEAK_MS - 1000:
            scream_channel, scream_duration = sound_effects.play_channel(INTRO_SCREAM)
            if scream_channel is not None:
                scream_started_at = now
                scream_duration_ms = max(1, round(scream_duration * 1000))
                scream_channel.set_volume(0.0)
        if scream_channel is not None:
            scream_progress = min(1.0, (now - scream_started_at) / scream_duration_ms)
            # The scream peaks as Hammy reaches the closest point of the lunge.
            envelope = math.sin(math.pi * scream_progress)
            scream_channel.set_volume(max(0.0, envelope))
        if not glass_break_played and elapsed >= PUNCH_IMPACT_MS - GLASS_SOUND_EARLY_MS:
            sound_effects.play(GLASS_BREAK_SOUND)
            glass_break_played = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit(0)

        screen.blit(backdrop, (0, 0))
        for x_ratio, y_ratio, phase in sparks:
            y = (y_ratio * height - elapsed * (.008 + phase * .003)) % height
            ember = round(45 + 35 * (0.5 + 0.5 * math.sin(elapsed * .002 + phase)))
            pygame.draw.circle(screen, (ember, round(ember * .48), round(ember * .32)),
                               (round(x_ratio * width), round(y)), max(1, round(min(size) * .002)))

        reveal = min(1.0, elapsed / 1650)
        center_x = width // 2
        lunge_progress = max(0.0, min(
            1.0, (elapsed - HAMMY_LUNGE_START_MS) / HAMMY_LUNGE_DURATION_MS))
        lunge = math.sin(math.pi * lunge_progress)
        lunge_frame = round(lunge * (len(lunge_images) - 1))
        current_image = lunge_images[lunge_frame]
        current_shadow = lunge_shadows[lunge_frame]
        mascot_center_y = round(height * (
            .34 + .012 * math.sin(elapsed * .0015) + .028 * lunge))
        lunge_shake = math.sin(elapsed * .07) * width * .006 * lunge
        mascot_center_x = round(center_x + lunge_shake)
        rect = current_image.get_rect(center=(mascot_center_x, mascot_center_y))
        shadow_rect = current_shadow.get_rect(
            center=(mascot_center_x + round(width * .008),
                    mascot_center_y + round(height * .018)))
        current_shadow.set_alpha(round(175 * reveal))
        current_image.set_alpha(round(255 * reveal))
        screen.blit(current_shadow, shadow_rect)
        screen.blit(current_image, rect)

        if reveal > .55:
            pulse = .65 + .35 * math.sin(elapsed * .004)
            eye_surface = pygame.Surface(size, pygame.SRCALPHA)
            for eye_x in (.45, .735):
                pos = (round(rect.left + current_image.get_width() * eye_x),
                       round(rect.top + current_image.get_height() * .357))
                pygame.draw.circle(eye_surface, (255, 45, 34, round(95 * reveal * pulse)),
                                   pos, max(2, round(mascot_size * .035)))
                pygame.draw.circle(eye_surface, (255, 173, 126, round(180 * reveal * pulse)),
                                   pos, max(1, round(mascot_size * .012)))
            screen.blit(eye_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        title_y = round(height * .68)
        for word, word_image in words.items():
            word_progress = max(0.0, min(1.0, (progress - onsets[word]) / .14))
            if word_progress <= 0:
                continue
            if word == "PUNCH":
                impact = max(0.0, 1.0 - abs(progress - .50) / .075)
                scale = 1.0 + .19 * impact
                rendered = pygame.transform.smoothscale(
                    word_image, (max(1, round(word_image.get_width() * scale)),
                                 max(1, round(word_image.get_height() * scale))))
                punch_center = (center_x, title_y + round(height * .105))
                if impact > 0:
                    shake = round(5 * impact)
                    punch_center = (punch_center[0] + random.randint(-shake, shake),
                                    punch_center[1] + random.randint(-shake, shake))
                    _crack_burst(screen, punch_center,
                                 max(1, round(rendered.get_width() * .68)),
                                 max(1, round(rendered.get_height() * .82)), impact)
            else:
                rendered = word_image
                line = 0 if word == "SMALL" else 2
                punch_center = (center_x, title_y + round(height * .105 * line))
            if word_progress < 1:
                rendered.set_alpha(round(255 * word_progress))
            shadow_image = shadow_words[word]
            if word == "PUNCH":
                shadow_image = pygame.transform.smoothscale(shadow_image, rendered.get_size())
            target = rendered.get_rect(center=punch_center)
            screen.blit(shadow_image, target.move(3, 5))
            screen.blit(rendered, target)

        if elapsed > INTRO_DURATION_MS - 450:
            fade = round(255 * min(1.0, (elapsed - (INTRO_DURATION_MS - 450)) / 450))
            overlay = pygame.Surface(size)
            overlay.fill((0, 0, 0))
            overlay.set_alpha(fade)
            screen.blit(overlay, (0, 0))

        pygame.display.flip()
        clock.tick(60)
        if elapsed >= INTRO_DURATION_MS:
            return

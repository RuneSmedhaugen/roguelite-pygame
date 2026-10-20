"""Load assets up front so the first menu and battle screens stay smooth."""

from core.characters import CHARACTERS
from ui.draw import preload_sprite_source
from ui.ui_renderer import preload_battle_background


def preload_startup_assets(screen, music, sound_effects, report_progress):
    tasks = []

    sprites = sorted({character["sprite"] for character in CHARACTERS if character.get("sprite")})
    for index, sprite in enumerate(sprites, start=1):
        tasks.append((
            f"Loading character art {index}/{len(sprites)}...",
            lambda name=sprite: preload_sprite_source(name),
        ))

    tasks.append(("Preparing the battle arena...", lambda: preload_battle_background(screen)))

    sounds = {
        "dodge.wav",
        "Loud-male-scream-sound-effect.mp3",
        "soundscrate-dropped-glass-1.mp3",
        "soundscrate-fighting-impact-punch.mp3",
        "soundscrate-fighting-punch-1.mp3",
        "soundscrate-fighting-punch-2.mp3",
        "soundscrate-fighting-punch-3.mp3",
    }
    for character in CHARACTERS:
        sounds.update(
            character.get(field)
            for field in ("intro_sound", "win_sound", "lose_sound")
            if character.get(field)
        )
    for sound in sorted(sounds):
        tasks.append((f"Loading sound: {sound}...", lambda name=sound: sound_effects.preload(name)))

    tasks.append(("Getting the music ready...", music.preload))

    total = len(tasks)
    for index, (message, load) in enumerate(tasks):
        report_progress(index / total, message)
        load()

    report_progress(1.0, "Ready!")

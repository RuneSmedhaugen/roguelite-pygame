"""Small sound-effect player with per-character optional clip paths."""

from pathlib import Path

import pygame

from core.assets import asset_path


class SoundEffects:
    def __init__(self, master=0.65, effects=0.8):
        self.master_volume = max(0.0, min(1.0, float(master)))
        self.effects_volume = max(0.0, min(1.0, float(effects)))
        self.cache = {}
        self.active_channels = []

    def set_audio_levels(self, master=None, effects=None, music=None):
        if master is not None:
            self.master_volume = max(0.0, min(1.0, float(master)))
        if effects is not None:
            self.effects_volume = max(0.0, min(1.0, float(effects)))
        for sound in self.cache.values():
            if sound is not None:
                sound.set_volume(self.master_volume * self.effects_volume)

    def play(self, filename):
        """Play a filename under assets/sounds/soundFX and return its duration."""
        if not filename or pygame.mixer.get_init() is None:
            return None

        relative_path = Path(filename)
        path = relative_path if relative_path.is_absolute() else asset_path("sounds", "soundFX", *relative_path.parts)
        cache_key = str(path)
        if cache_key not in self.cache:
            try:
                self.cache[cache_key] = pygame.mixer.Sound(str(path))
            except (pygame.error, OSError) as error:
                print(f"Could not load sound effect '{path}': {error}")
                self.cache[cache_key] = None

        sound = self.cache[cache_key]
        if sound is None:
            return None
        sound.set_volume(self.master_volume * self.effects_volume)
        channel = sound.play()
        if channel is not None:
            self.active_channels = [active for active in self.active_channels if active.get_busy()]
            self.active_channels.append(channel)
        return sound.get_length() if channel is not None else None

    def pause(self):
        self.active_channels = [channel for channel in self.active_channels if channel.get_busy()]
        for channel in self.active_channels:
            channel.pause()

    def resume(self):
        for channel in self.active_channels:
            channel.unpause()
        self.active_channels = [channel for channel in self.active_channels if channel.get_busy()]

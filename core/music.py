"""Playlist playback for the game's background music."""

from pathlib import Path

import pygame


class MusicPlaylist:
    SUPPORTED_EXTENSIONS = {".mp3", ".ogg", ".wav", ".m4a"}

    def __init__(self, folder=None):
        self.folder = Path(folder) if folder else Path(__file__).resolve().parent.parent / "assets" / "sounds" / "music"
        self.ended_event = pygame.event.custom_type()
        self.tracks = []
        self.current_index = -1
        self.master_volume = 0.65
        self.music_volume = 0.45
        self.effects_volume = 0.8
        self.enabled = pygame.mixer.get_init() is not None
        if self.enabled:
            pygame.mixer.music.set_endevent(self.ended_event)
            self._apply_music_volume()
        self.refresh()

    @property
    def audio_levels(self):
        return {
            "master": self.master_volume,
            "music": self.music_volume,
            "effects": self.effects_volume,
        }

    @property
    def effective_effects_volume(self):
        """Volume to apply to future sound effects, including the master level."""
        return self.master_volume * self.effects_volume

    def set_audio_levels(self, master=None, music=None, effects=None):
        if master is not None:
            self.master_volume = max(0.0, min(1.0, float(master)))
        if music is not None:
            self.music_volume = max(0.0, min(1.0, float(music)))
        if effects is not None:
            self.effects_volume = max(0.0, min(1.0, float(effects)))
        self._apply_music_volume()

    def _apply_music_volume(self):
        if self.enabled:
            pygame.mixer.music.set_volume(self.master_volume * self.music_volume)

    def refresh(self):
        """Pick up supported audio files added to the music folder."""
        if self.folder.is_dir():
            self.tracks = sorted(
                path for path in self.folder.iterdir()
                if path.is_file() and path.suffix.lower() in self.SUPPORTED_EXTENSIONS
            )
        else:
            self.tracks = []

    def start(self):
        if not self.enabled or not self.tracks:
            return
        self.current_index = 0
        self._play_current()

    def play_next(self):
        # Rescan at each transition so newly added files are included without
        # needing to change the playlist code.
        previous = self.tracks[self.current_index] if 0 <= self.current_index < len(self.tracks) else None
        self.refresh()
        if not self.tracks:
            self.current_index = -1
            return
        if previous in self.tracks:
            self.current_index = (self.tracks.index(previous) + 1) % len(self.tracks)
        else:
            self.current_index = 0
        self._play_current()

    def _play_current(self):
        try:
            pygame.mixer.music.load(str(self.tracks[self.current_index]))
            self._apply_music_volume()
            pygame.mixer.music.play()
        except pygame.error as exc:
            # Skip a file that the active mixer backend cannot decode.
            print(f"Could not play music '{self.tracks[self.current_index].name}': {exc}")
            self.tracks.pop(self.current_index)
            if self.tracks:
                self.current_index %= len(self.tracks)
                self._play_current()
            else:
                self.current_index = -1


"""Playlist playback for the game's background music."""

from pathlib import Path
import random

import pygame

from core.assets import asset_path


class MusicPlaylist:
    SUPPORTED_EXTENSIONS = {".mp3", ".ogg", ".wav", ".m4a"}

    def __init__(self, folder=None):
        self.folder = Path(folder) if folder else asset_path("sounds", "music")
        self.ended_event = pygame.event.custom_type()
        self.tracks = []
        self._discovered_tracks = set()
        self.current_index = -1
        self.preloaded_track = None
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
        """Keep one shuffled playback order, adding newly discovered songs at its end."""
        if self.folder.is_dir():
            discovered = {
                path for path in self.folder.iterdir()
                if path.is_file() and path.suffix.lower() in self.SUPPORTED_EXTENSIONS
            }
        else:
            discovered = set()

        if discovered == self._discovered_tracks:
            return

        # Preserve the current cycle's order across refreshes. New files join
        # at the end in random order; removed files simply leave the cycle.
        self.tracks = [track for track in self.tracks if track in discovered]
        added = list(discovered - self._discovered_tracks)
        random.shuffle(added)
        self.tracks.extend(added)
        self._discovered_tracks = discovered

        if self.current_index >= len(self.tracks):
            self.current_index = len(self.tracks) - 1

    def start(self):
        if not self.enabled or not self.tracks:
            return
        self.current_index = 0
        self._play_current(fade_ms=1200)

    def preload(self):
        """Load the opening track without starting playback."""
        if not self.enabled:
            return
        self.refresh()
        while self.tracks:
            try:
                pygame.mixer.music.load(str(self.tracks[0]))
                self.preloaded_track = self.tracks[0]
                return
            except pygame.error as exc:
                print(f"Could not preload music '{self.tracks[0].name}': {exc}")
                self.tracks.pop(0)
        self.preloaded_track = None

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
        self.preloaded_track = None
        self._play_current()

    def _play_current(self, fade_ms=0):
        try:
            track = self.tracks[self.current_index]
            if self.preloaded_track != track:
                pygame.mixer.music.load(str(track))
            self.preloaded_track = None
            self._apply_music_volume()
            pygame.mixer.music.play(fade_ms=fade_ms)
        except pygame.error as exc:
            # Skip a file that the active mixer backend cannot decode.
            print(f"Could not play music '{self.tracks[self.current_index].name}': {exc}")
            self.tracks.pop(self.current_index)
            if self.tracks:
                self.current_index %= len(self.tracks)
                self._play_current()
            else:
                self.current_index = -1


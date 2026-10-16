"""Display settings screen and the display modes it can request."""

import pygame
from ui.layout import font, scaled, settings_layout


DISPLAY_MODES = (
    ("fullscreen", "Fullscreen"),
    ("borderless", "Borderless window"),
    ("windowed", "Windowed"),
)

FALLBACK_RESOLUTIONS = (
    (1280, 720),
    (1366, 768),
    (1600, 900),
    (1920, 1080),
)


def display_count():
    try:
        return max(1, pygame.display.get_num_displays())
    except pygame.error:
        return 1


def display_label(index):
    return f"Display {index + 1}" + (" (default)" if index == 0 else "")


def desktop_size(index):
    try:
        sizes = pygame.display.get_desktop_sizes()
    except pygame.error:
        sizes = []
    if not sizes:
        return None
    return sizes[index] if index < len(sizes) else sizes[0]


def supported_resolutions(display_index=0):
    """Return unique display modes reported by SDL, with sensible fallbacks."""
    try:
        modes = pygame.display.list_modes(flags=pygame.FULLSCREEN, display=display_index)
    except pygame.error:
        modes = []

    if modes == -1 or not modes:
        modes = FALLBACK_RESOLUTIONS

    result = []
    for mode in modes:
        if len(mode) == 2 and mode[0] > 0 and mode[1] > 0 and mode not in result:
            result.append(tuple(mode))

    if not result:
        result.extend(FALLBACK_RESOLUTIONS)
    current_size = desktop_size(display_index)
    if current_size and current_size not in result:
        result.append(current_size)
    return sorted(result, key=lambda size: (size[0] * size[1], size[0]))


class SettingsScreen:
    def __init__(self, on_audio_change=None, audio_levels=None):
        self.monitor_count = display_count()
        self.monitor_index = 0
        self.resolutions = supported_resolutions(self.monitor_index)
        self.mode_index = 0
        self.resolution_index = 0
        self.open_dropdown = None
        self.dropdown_scroll = 0
        self.dropdown_visible_count = 1
        self.on_audio_change = on_audio_change
        self.audio_levels = dict(audio_levels or {"master": 0.65, "music": 0.45, "effects": 0.8})

    @property
    def mode(self):
        return DISPLAY_MODES[self.mode_index][0]

    @property
    def resolution(self):
        return self.resolutions[self.resolution_index]

    def sync(self, mode, size, monitor_index=None):
        mode_names = [item[0] for item in DISPLAY_MODES]
        if mode in mode_names:
            self.mode_index = mode_names.index(mode)
        if monitor_index is not None and 0 <= monitor_index < self.monitor_count:
            self.monitor_index = monitor_index
            self.resolutions = supported_resolutions(self.monitor_index)
        if size not in self.resolutions:
            self.resolutions.append(tuple(size))
            self.resolutions.sort(key=lambda value: (value[0] * value[1], value[0]))
        self.resolution_index = self.resolutions.index(tuple(size))

    def _layout(self, screen):
        return settings_layout(screen)

    def _options(self, key):
        if key == "mode":
            return [label for _, label in DISPLAY_MODES]
        if key == "monitor":
            return [display_label(index) for index in range(self.monitor_count)]
        return [f"{width} × {height}" for width, height in self.resolutions]

    def _selected_index(self, key):
        if key == "mode":
            return self.mode_index
        if key == "monitor":
            return self.monitor_index
        return self.resolution_index

    def _set_monitor(self, index):
        old_resolution = self.resolution
        self.monitor_index = index
        self.resolutions = supported_resolutions(index)
        if old_resolution in self.resolutions:
            self.resolution_index = self.resolutions.index(old_resolution)
            return
        preferred = desktop_size(index)
        if preferred in self.resolutions:
            self.resolution_index = self.resolutions.index(preferred)
        else:
            self.resolution_index = len(self.resolutions) - 1

    def _dropdown(self, screen):
        if self.open_dropdown is None:
            return pygame.Rect(0, 0, 0, 0), []

        panel, mode_rect, monitor_rect, resolution_rect, _, _, _, back_rect, _ = self._layout(screen)
        selector = {
            "mode": mode_rect,
            "monitor": monitor_rect,
            "resolution": resolution_rect,
        }[self.open_dropdown]
        options = self._options(self.open_dropdown)
        item_height = scaled(screen, 38)
        popup_top = selector.bottom + scaled(screen, 6)
        limit_bottom = min(panel.bottom - scaled(screen, 12), back_rect.top - scaled(screen, 8))
        available = limit_bottom - popup_top
        visible_count = max(1, min(5, available // item_height, len(options)))
        self.dropdown_visible_count = visible_count
        self.dropdown_scroll = min(self.dropdown_scroll, max(0, len(options) - visible_count))
        popup = pygame.Rect(selector.left, popup_top, selector.width, visible_count * item_height)
        rows = [
            pygame.Rect(popup.left, popup.top + index * item_height, popup.width, item_height)
            for index in range(visible_count)
        ]
        return popup, rows

    def handle_click(self, screen, position):
        panel, mode_rect, monitor_rect, resolution_rect, _, _, _, back_rect, apply_rect = self._layout(screen)
        popup, option_rects = self._dropdown(screen)

        if popup.collidepoint(position):
            for offset, rect in enumerate(option_rects):
                if rect.collidepoint(position):
                    index = self.dropdown_scroll + offset
                    if self.open_dropdown == "mode":
                        self.mode_index = index
                    elif self.open_dropdown == "monitor":
                        self._set_monitor(index)
                    else:
                        self.resolution_index = index
                    self.open_dropdown = None
                    self.dropdown_scroll = 0
                    return None, None

        for key, rect in (("mode", mode_rect), ("monitor", monitor_rect), ("resolution", resolution_rect)):
            if rect.collidepoint(position):
                self.open_dropdown = None if self.open_dropdown == key else key
                self.dropdown_scroll = 0
                if self.open_dropdown == "resolution":
                    visible = max(1, len(self._dropdown(screen)[1]))
                    self.dropdown_scroll = max(0, min(self.resolution_index - visible // 2, len(self.resolutions) - visible))
                return None, None

        self.open_dropdown = None
        self.dropdown_scroll = 0
        if back_rect.collidepoint(position):
            return "back", None
        if apply_rect.collidepoint(position):
            return "apply", (self.mode, self.resolution, self.monitor_index)
        return None, None

    def handle_scroll(self, amount):
        if self.open_dropdown != "resolution":
            return
        self.dropdown_scroll = max(0, min(
            self.dropdown_scroll - amount,
            max(0, len(self.resolutions) - self.dropdown_visible_count),
        ))

    def handle_audio_drag(self, screen, position, mouse_held):
        if not mouse_held:
            return False
        layout = self._layout(screen)
        slider_rects = dict(zip(("master", "music", "effects"), layout[4:7]))
        for key, rect in slider_rects.items():
            hit_rect = rect.inflate(0, scaled(screen, 12))
            if hit_rect.collidepoint(position):
                value = max(0.0, min(1.0, (position[0] - rect.left) / max(1, rect.width)))
                self.audio_levels[key] = value
                if self.on_audio_change:
                    self.on_audio_change(**self.audio_levels)
                return True
        return False

    def draw(self, screen, mouse_pos):
        screen.fill((15, 15, 25))
        panel, mode_rect, monitor_rect, resolution_rect, master_rect, music_rect, effects_rect, back_rect, apply_rect = self._layout(screen)
        pygame.draw.rect(screen, (30, 30, 46), panel, border_radius=scaled(screen, 14))

        title_font = font(screen, 54)
        label_font = font(screen, 26)
        value_font = font(screen, 32)
        small_font = font(screen, 22)

        title = title_font.render("DISPLAY SETTINGS", True, (245, 245, 255))
        screen.blit(title, title.get_rect(center=(panel.centerx, panel.top + scaled(screen, 44))))

        selectors = (
            ("Display mode", mode_rect, dict(DISPLAY_MODES)[self.mode], "mode"),
            ("Monitor", monitor_rect, display_label(self.monitor_index), "monitor"),
            ("Resolution", resolution_rect, f"{self.resolution[0]} × {self.resolution[1]}", "resolution"),
        )
        for label, rect, value, key in selectors:
            screen.blit(label_font.render(label, True, (180, 185, 205)), (rect.left, rect.top - scaled(screen, 28)))
            color = (75, 85, 120) if rect.collidepoint(mouse_pos) or self.open_dropdown == key else (48, 53, 75)
            pygame.draw.rect(screen, color, rect, border_radius=scaled(screen, 8))
            screen.blit(value_font.render(value, True, (255, 255, 255)), (rect.left + scaled(screen, 16), rect.top + scaled(screen, 11)))
            arrow_x = rect.right - scaled(screen, 22)
            arrow_y = rect.centery
            arrow_size = scaled(screen, 6)
            points = (
                ((arrow_x - arrow_size, arrow_y + arrow_size // 2),
                 (arrow_x, arrow_y - arrow_size // 2),
                 (arrow_x + arrow_size, arrow_y + arrow_size // 2))
                if self.open_dropdown == key else
                ((arrow_x - arrow_size, arrow_y - arrow_size // 2),
                 (arrow_x, arrow_y + arrow_size // 2),
                 (arrow_x + arrow_size, arrow_y - arrow_size // 2))
            )
            pygame.draw.lines(screen, (190, 195, 215), False, points, scaled(screen, 2))

        sound_title = small_font.render("SOUND", True, (220, 225, 240))
        screen.blit(sound_title, (master_rect.left, master_rect.top - scaled(screen, 38)))
        self._draw_slider(screen, master_rect, "Master", self.audio_levels["master"], mouse_pos, small_font)
        self._draw_slider(screen, music_rect, "Music", self.audio_levels["music"], mouse_pos, small_font)
        self._draw_slider(screen, effects_rect, "Effects", self.audio_levels["effects"], mouse_pos, small_font)

        self._draw_button(screen, back_rect, "BACK", mouse_pos, small_font)
        self._draw_button(screen, apply_rect, "APPLY", mouse_pos, small_font)

        popup, option_rects = self._dropdown(screen)
        if option_rects:
            options = self._options(self.open_dropdown)
            selected_index = self._selected_index(self.open_dropdown)
            screen.set_clip(panel)
            pygame.draw.rect(screen, (22, 25, 39), popup, border_radius=scaled(screen, 6))
            for offset, rect in enumerate(option_rects):
                index = self.dropdown_scroll + offset
                hovered = rect.collidepoint(mouse_pos)
                if hovered or index == selected_index:
                    pygame.draw.rect(screen, (73, 86, 125) if hovered else (52, 63, 95), rect)
                option = small_font.render(options[index], True, (255, 255, 255))
                screen.blit(option, (rect.left + scaled(screen, 16), rect.centery - option.get_height() // 2))
            if len(options) > len(option_rects):
                track_width = scaled(screen, 4)
                track = pygame.Rect(popup.right - scaled(screen, 8), popup.top, track_width, popup.height)
                pygame.draw.rect(screen, (55, 60, 78), track, border_radius=track_width)
                thumb_height = max(scaled(screen, 18), round(popup.height * len(option_rects) / len(self.resolutions)))
                scroll_range = max(1, len(self.resolutions) - len(option_rects))
                thumb_y = popup.top + round((popup.height - thumb_height) * self.dropdown_scroll / scroll_range)
                pygame.draw.rect(screen, (170, 180, 205), (track.left, thumb_y, track.width, thumb_height), border_radius=track_width)
            screen.set_clip(None)

    @staticmethod
    def _draw_button(screen, rect, label, mouse_pos, font):
        color = (90, 105, 150) if rect.collidepoint(mouse_pos) else (62, 72, 105)
        pygame.draw.rect(screen, color, rect, border_radius=scaled(screen, 8))
        text = font.render(label, True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=rect.center))

    @staticmethod
    def _draw_slider(screen, rect, label, value, mouse_pos, text_font):
        label_surface = text_font.render(label, True, (180, 185, 205))
        screen.blit(label_surface, (rect.left, rect.top - scaled(screen, 20)))
        percent = text_font.render(f"{round(value * 100)}%", True, (225, 230, 245))
        screen.blit(percent, percent.get_rect(midright=(rect.right, rect.top - scaled(screen, 20))))

        center_y = rect.centery
        start_x = rect.left + scaled(screen, 5)
        end_x = rect.right - scaled(screen, 5)
        knob_x = round(start_x + (end_x - start_x) * value)
        pygame.draw.line(screen, (65, 70, 92), (start_x, center_y), (end_x, center_y), scaled(screen, 6))
        pygame.draw.line(screen, (116, 151, 220), (start_x, center_y), (knob_x, center_y), scaled(screen, 6))
        knob_color = (230, 236, 255) if rect.collidepoint(mouse_pos) else (195, 210, 245)
        pygame.draw.circle(screen, knob_color, (knob_x, center_y), scaled(screen, 9))

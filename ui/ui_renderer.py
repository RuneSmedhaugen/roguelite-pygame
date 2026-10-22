import pygame

from core.assets import asset_path
from ui.layout import scaled
from ui.menu_antics import MenuAntics
from ui.draw import (
    draw_menu,
    draw_round,
    draw_stats,
    draw_game_over,
    draw_character_select,
    draw_upgrades,
    draw_pause_button,
    draw_pause_menu,
    draw_global_feedback_button,
    draw_life_runes,
    draw_battle_outcome_labels,
    draw_feedback_screen,
    draw_changelog_screen,
    draw_mode_select,
    draw_passive_status,
)
from singleplayer.achievements_ui import draw_achievements_screen, draw_achievement_toast


_BATTLE_BACKGROUND = None
_BATTLE_BACKGROUND_SCALED = {}


def preload_battle_background(screen):
    """Decode and scale the battle background before the first battle frame."""
    global _BATTLE_BACKGROUND

    if _BATTLE_BACKGROUND is None:
        _BATTLE_BACKGROUND = pygame.image.load(
            str(asset_path("background", "Rune_bakgrunn.png"))
        ).convert()

    size = screen.get_size()
    if size not in _BATTLE_BACKGROUND_SCALED:
        _BATTLE_BACKGROUND_SCALED[size] = pygame.transform.smoothscale(_BATTLE_BACKGROUND, size)
    return _BATTLE_BACKGROUND_SCALED[size]


class UIRenderer:
    def __init__(self):
        self.menu_antics = MenuAntics()

    def _draw_battle_background(self, screen):
        screen.blit(preload_battle_background(screen), (0, 0))

    def draw(self, game, screen, mouse_pos):
        state = game.state

        if state == "menu":
            draw_menu(game, screen, self.menu_antics)

        elif state == "mode_select":
            draw_mode_select(screen, mouse_pos)

        elif state in ("feedback_type", "feedback_form"):
            draw_feedback_screen(
                screen,
                state,
                game.feedback_kind,
                game.feedback_title,
                game.feedback_message,
                game.feedback_severity,
                game.feedback_focus,
                game.feedback_severity_open,
                game.feedback_status,
            )

        elif state == "changelog":
            draw_changelog_screen(screen, game.changelog_entries, game.changelog_loading, game.changelog_error)

        elif state == "achievements":
            draw_achievements_screen(screen, game, mouse_pos)

        elif state == "settings":
            game.settings_screen.draw(screen, mouse_pos)

        elif state == "select":
            draw_character_select(
                screen,
                game.character_choices,
                game.hovered_index,
                mouse_pos,
                confirmation_index=game.pending_character_index,
            )

        elif state in ("battle_intro", "battle"):
            self._draw_battle_background(screen)
            draw_round(screen, game.round)

            if game.battle:
                frozen_time = game.pause_started_at if game.pause_open else None
                if state == "battle_intro":
                    now = frozen_time if frozen_time is not None else pygame.time.get_ticks()
                    elapsed = now - game.battle_intro_started_at
                    progress = min(1.0, elapsed / max(1, game.battle_intro_duration_ms))
                    game.battle.draw_intro(
                        screen,
                        game.battle_intro_character,
                        progress,
                        animation_time=now,
                    )
                else:
                    game.battle.draw(screen, animation_time=frozen_time)

            # player + enemy stats
            stats_y = scaled(screen, 70)
            draw_stats(
                screen,
                game.player,
                scaled(screen, 28),
                stats_y,
                game.battle.combat.resolve_display_stats(game.player),
            )
            draw_stats(
                screen,
                game.enemy,
                screen.get_width() - scaled(screen, 240),
                stats_y,
                game.battle.combat.resolve_display_stats(game.enemy),
            )
            draw_passive_status(screen, game.player, "left")
            draw_passive_status(screen, game.enemy, "right")

        elif state == "battle_result":
            self._draw_battle_background(screen)
            animation_time = game.pause_started_at if game.pause_open else pygame.time.get_ticks()
            elapsed = animation_time - game.result_started_at
            progress = min(1.0, elapsed / max(1, game.result_duration_ms))
            if game.battle:
                game.battle.draw_outcome(screen, game.result, progress)
            draw_battle_outcome_labels(screen, game.result)
            draw_life_runes(screen, game.lives)

        elif state == "upgrade":
            game.upgrade_rects = draw_upgrades(screen, game.upgrades, game.result)

        elif state == "game_over":
            draw_game_over(screen, game, mouse_pos, won=False)

        elif state == "game_win":
            draw_game_over(screen, game, mouse_pos, won=True)

        if (game.achievement_toast is not None and not game.pause_open
                and state in ("battle_result", "game_over", "game_win")):
            draw_achievement_toast(screen, game.achievement_toast)

        if state in ("battle_intro", "battle", "battle_result", "upgrade"):
            draw_life_runes(screen, game.lives)
            draw_pause_button(screen, mouse_pos)
        if game.pause_open:
            draw_pause_menu(screen, mouse_pos)
        elif state not in ("feedback_type", "feedback_form"):
            draw_global_feedback_button(screen, mouse_pos)

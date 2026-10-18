import pygame

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
    draw_life_runes,
    draw_battle_outcome_labels,
    draw_feedback_screen,
)


_BATTLE_BACKGROUND = None
_BATTLE_BACKGROUND_SCALED = {}


class UIRenderer:
    def __init__(self):
        self.menu_antics = MenuAntics()

    def _draw_battle_background(self, screen):
        global _BATTLE_BACKGROUND

        if _BATTLE_BACKGROUND is None:
            _BATTLE_BACKGROUND = pygame.image.load(
                "assets/background/Rune_bakgrunn.png"
            ).convert()

        size = screen.get_size()
        background = _BATTLE_BACKGROUND_SCALED.get(size)
        if background is None:
            background = pygame.transform.smoothscale(_BATTLE_BACKGROUND, size)
            _BATTLE_BACKGROUND_SCALED[size] = background
        screen.blit(background, (0, 0))

    def draw(self, game, screen, mouse_pos):
        state = game.state

        if state == "menu":
            draw_menu(game, screen, self.menu_antics)

        elif state in ("feedback_type", "feedback_form"):
            draw_feedback_screen(
                screen,
                state,
                game.feedback_kind,
                game.feedback_message,
                game.feedback_status,
            )

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

        elif state == "battle":
            self._draw_battle_background(screen)
            draw_round(screen, game.round)

            if game.battle:
                frozen_time = game.pause_started_at if game.pause_open else None
                game.battle.draw(screen, animation_time=frozen_time)

            # player + enemy stats
            stats_y = scaled(screen, 70)
            draw_stats(screen, game.player, scaled(screen, 28), stats_y)
            draw_stats(screen, game.enemy, screen.get_width() - scaled(screen, 240), stats_y)

        elif state == "battle_result":
            self._draw_battle_background(screen)
            elapsed = pygame.time.get_ticks() - game.result_started_at
            progress = min(1.0, elapsed / 2200)
            if game.battle:
                game.battle.draw_outcome(screen, game.result, progress)
            draw_battle_outcome_labels(screen, game.result)
            draw_life_runes(screen, game.lives)

        elif state == "result":
            draw_game_over(screen, game, mouse_pos)

        elif state == "upgrade":
            game.upgrade_rects = draw_upgrades(screen, game.upgrades, game.result)

        elif state == "game_over":
            draw_game_over(screen, game, mouse_pos)

        if state in ("battle", "upgrade"):
            draw_life_runes(screen, game.lives)
            draw_pause_button(screen, mouse_pos)
        if game.pause_open:
            draw_pause_menu(screen, mouse_pos)

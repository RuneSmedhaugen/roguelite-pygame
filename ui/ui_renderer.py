import pygame

from ui.layout import scaled
from ui.draw import (
    draw_menu,
    draw_round,
    draw_stats,
    draw_game_over,
    draw_character_select,
    draw_upgrades
)


_BATTLE_BACKGROUND = None
_BATTLE_BACKGROUND_SCALED = {}


class UIRenderer:
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
            draw_menu(game, screen)

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
                game.battle.draw(screen)

            # player + enemy stats
            stats_y = screen.get_height() - scaled(screen, 200)
            draw_stats(screen, game.player, scaled(screen, 80), stats_y)
            draw_stats(screen, game.enemy, screen.get_width() - scaled(screen, 300), stats_y)

        elif state == "result":
            draw_game_over(screen)

        elif state == "upgrade":
            game.upgrade_rects = draw_upgrades(screen, game.upgrades, game.result)

        elif state == "game_over":
            draw_game_over(screen)

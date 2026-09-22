import pygame
from ui.draw import (
    draw_menu,
    draw_settings,
    draw_round,
    draw_stats,
    draw_result,
    draw_character_select,
    draw_upgrades
)

class UIRenderer:
    def draw(self, game, screen, mouse_pos):
        state = game.state

        if state == "menu":
            draw_menu(game, screen)

        elif state == "settings":
            draw_settings(game, screen)

        elif state == "select":
            draw_character_select(
                screen,
                game.character_choices,
                game.select_ui.selected_index if hasattr(game.select_ui, "selected_index") else None,
                mouse_pos
            )

        elif state == "battle":
            screen.fill((10, 10, 20))
            draw_round(screen, game.round)

            # player + enemy stats
            draw_stats(screen, game.player, 80, 400)
            draw_stats(screen, game.enemy, 500, 400)

        elif state == "result":
            draw_result(screen, game.result)

        elif state == "upgrade":
            draw_upgrades(screen, game.upgrades, True)
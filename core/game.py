import pygame

from core.entities import Character
from core.battle import Battle
from core.enemy_factory import generate_enemy
from core.upgrades import get_random_upgrades
from core.character_factory import build_character
from core.character_factory import get_random_characters

from ui.draw import draw_character_select
from ui.layout import menu_buttons, pause_layout, select_back_button, selection_confirm_buttons


class Game:
    def __init__(self, music=None):
        from ui.ui_renderer import UIRenderer
        from ui.settings import SettingsScreen
        self.music = music
        self.ui = UIRenderer()
        self.settings_screen = SettingsScreen(
            on_audio_change=music.set_audio_levels if music else None,
            audio_levels=music.audio_levels if music else None,
        )
        self.display_mode = "fullscreen"
        self.display_index = 0
        self.display_size = pygame.display.get_surface().get_size()
        self.settings_screen.sync(self.display_mode, self.display_size, self.display_index)
        self.display_request = None
        self.exit_requested = False

        self.round = 1
        self.state = "menu"

        # data
        self.lives = 5
        self.character_choices = []
        self.selected_index = None
        self.hovered_index = None
        self.pending_character_index = None
        self.player = None
        self.enemy = None
        self.battle = None
        self.result = None
        self.result_started_at = None
        self.click_lock = False
        self.selected_upgrade = None
        self.pause_open = False
        self.pause_started_at = None
        self.pause_return_state = None
        self.settings_from_pause = False
        self.escape_was_down = False

        # upgrades
        self.upgrades = []

        # init choices immediately (so select screen works)
        self.character_choices = get_random_characters(5)

    # -------------------------
    # START GAME
    # -------------------------
    def start_game_with_character(self, index):
        raw = self.character_choices[index]

        self.player = build_character(raw, x=150, y=250)
        self.player.color = (50, 150, 255)

        self.enemy = generate_enemy(self.round)
        self.battle = Battle(self.player, self.enemy)

        self.state = "battle"

    # -------------------------
    # UPGRADES
    # -------------------------
    def start_upgrade(self):
        self.upgrades = get_random_upgrades(3)
        self.upgrade_rects = []

    def reset_run(self):
        self.round = 1
        self.lives = 5
        self.player = None
        self.enemy = None
        self.battle = None
        self.result = None
        self.result_started_at = None
        self.pending_character_index = None
        self.hovered_index = None
        self.pause_open = False
        self.pause_started_at = None
        self.pause_return_state = None
        self.settings_from_pause = False
        self.state = "menu"

    def _leave_pause_settings(self):
        if self.settings_from_pause:
            self.state = self.pause_return_state
            self.pause_return_state = None
            self.settings_from_pause = False
            self.pause_open = True
        else:
            self.state = "menu"

    def _open_pause(self):
        if not self.pause_open:
            self.pause_open = True
            self.pause_started_at = pygame.time.get_ticks()

    def _resume_from_pause(self):
        if self.pause_started_at is not None:
            paused_for = pygame.time.get_ticks() - self.pause_started_at
            if self.battle is not None:
                self.battle.player_last_attack += paused_for
                self.battle.enemy_last_attack += paused_for
                for combat_text in self.battle.combat_texts:
                    combat_text.created_at += paused_for
                for animation in (*self.battle.attack_animations.values(), *self.battle.reactions.values()):
                    animation["start"] += paused_for
                for effect in (*self.battle.effects.particles, *self.battle.effects.rings):
                    effect["born"] += paused_for
        self.pause_open = False
        self.pause_started_at = None

    
    # -------------------------
    # UPDATE LOOP (LOGIC ONLY)
    # -------------------------
    def update(self, keys, mouse_pos, mouse_click, screen=None):
        escape_down = bool(keys[pygame.K_ESCAPE])
        escape_pressed = escape_down and not self.escape_was_down
        self.escape_was_down = escape_down

        if not mouse_click:
            self.click_lock = False

        # MENU
        if self.state == "menu":
            if mouse_click and not self.click_lock:
                self.click_lock = True

                play_button, settings_button, exit_button = menu_buttons(screen or pygame.display.get_surface())

                if play_button.collidepoint(mouse_pos):
                    print("CLICK PLAY")
                    self.state = "select"
                elif settings_button.collidepoint(mouse_pos):
                    self.settings_from_pause = False
                    self.state = "settings"
                elif exit_button.collidepoint(mouse_pos):
                    self.exit_requested = True

            return

        if self.state == "settings":
            if escape_pressed:
                self._leave_pause_settings()
                return
            if screen is not None and self.settings_screen.handle_audio_drag(screen, mouse_pos, mouse_click):
                self.click_lock = True
                return
            if mouse_click and not self.click_lock and screen is not None:
                self.click_lock = True
                action, request = self.settings_screen.handle_click(screen, mouse_pos)
                if action == "back":
                    self._leave_pause_settings()
                elif action == "apply":
                    self.display_request = request
            return

        # SELECT
        if self.state == "select":
            layout_screen = screen or pygame.display.get_surface()
            if self.pending_character_index is not None:
                if mouse_click and not self.click_lock:
                    self.click_lock = True
                    _, start_button, back_button = selection_confirm_buttons(layout_screen)
                    if start_button.collidepoint(mouse_pos):
                        selected = self.pending_character_index
                        self.pending_character_index = None
                        self.start_game_with_character(selected)
                    elif back_button.collidepoint(mouse_pos):
                        self.pending_character_index = None
                return

            rects = draw_character_select(
                layout_screen,
                self.character_choices,
                None,
                mouse_pos,
                dry_run=True
            )
            self.hovered_index = next(
                (index for index, rect in enumerate(rects) if rect.collidepoint(mouse_pos)),
                None,
            )

            if mouse_click and not self.click_lock and select_back_button(layout_screen).collidepoint(mouse_pos):
                self.click_lock = True
                self.hovered_index = None
                self.state = "menu"
                return

            if mouse_click and not self.click_lock and rects:
                for i, r in enumerate(rects):
                    if r.collidepoint(mouse_pos):
                        self.click_lock = True
                        self.pending_character_index = i
                        return
            return

        if self.state in ("battle", "upgrade"):
            if escape_pressed:
                if self.pause_open:
                    self._resume_from_pause()
                else:
                    self._open_pause()
                    return

            if self.pause_open:
                if mouse_click and not self.click_lock and screen is not None:
                    self.click_lock = True
                    _, _, continue_button, settings_button, menu_button, close_button = pause_layout(screen)
                    if continue_button.collidepoint(mouse_pos) or close_button.collidepoint(mouse_pos):
                        self._resume_from_pause()
                    elif settings_button.collidepoint(mouse_pos):
                        self.pause_return_state = self.state
                        self.settings_from_pause = True
                        self.pause_open = False
                        self.state = "settings"
                    elif menu_button.collidepoint(mouse_pos):
                        self.reset_run()
                return

            if mouse_click and not self.click_lock and screen is not None:
                pause_button, *_ = pause_layout(screen)
                if pause_button.collidepoint(mouse_pos):
                    self.click_lock = True
                    self._open_pause()
                    return

        # BATTLE
        if self.state == "battle":
            if not self.battle.finished:
                self.battle.update()
            else:
                self.result = self.battle.winner

                if self.result == "enemy":
                    self.lives -= 1
                    print (f"LIFE LOST! Lives remaining: {self.lives}")

                self.result_started_at = pygame.time.get_ticks()
                self.state = "battle_result"
            return

        if self.state == "battle_result":
            if pygame.time.get_ticks() - self.result_started_at >= 2200:
                if self.lives <= 0:
                    self.state = "game_over"
                else:
                    self.start_upgrade()
                    self.state = "upgrade"
            return

        # UPGRADE
        if self.state == "upgrade":

            if mouse_click and not self.click_lock:
                self.click_lock = True

                for i, r in enumerate(self.upgrade_rects):
                    if r.collidepoint(mouse_pos):

                        upg = self.upgrades[i]

                        # -------- BEFORE SNAPSHOT --------
                        before = {
                            "hp": self.player.hp,
                            "max_hp": self.player.max_hp,
                            "atk_min": self.player.atk_min,
                            "atk_max": self.player.atk_max,
                            "crit": self.player.crit,
                            "dodge": self.player.dodge,
                            "lifesteal": self.player.lifesteal,
                            "attack_speed": self.player.attack_speed,
                            "armor": self.player.armor,
                        }

                        print("\n===== UPGRADE START =====")
                        print("SELECTED:", upg)
                        print("BEFORE:", before)

                        # APPLY
                        self.player.apply_upgrade(upg)

                        # -------- AFTER SNAPSHOT --------
                        after = {
                            "hp": self.player.hp,
                            "max_hp": self.player.max_hp,
                            "atk_min": self.player.atk_min,
                            "atk_max": self.player.atk_max,
                            "crit": self.player.crit,
                            "dodge": self.player.dodge,
                            "lifesteal": self.player.lifesteal,
                            "attack_speed": self.player.attack_speed,
                            "armor": self.player.armor,
                        }

                        print("AFTER: ", after)

                        # -------- DIFF HIGHLIGHT --------
                        print("CHANGES:")
                        for k in before:
                            if before[k] != after[k]:
                                print(f"  {k}: {before[k]} -> {after[k]}")

                        print("===== UPGRADE END =====\n")

                        self.state = "next"
                        break

            return

        # NEXT ROUND
        if self.state == "next":
            self.round += 1
            self.player.hp = self.player.max_hp
            self.enemy = generate_enemy(self.round)
            self.battle = Battle(self.player, self.enemy)
            self.state = "battle"
            return

        if self.state == "game_over":
            if mouse_click and not self.click_lock:
                self.click_lock = True
                self.reset_run()
            return

    # -------------------------
    # DRAW LOOP (RENDER ONLY)
    # -------------------------
    def draw(self, screen, mouse_pos):
        self.ui.draw(self, screen, mouse_pos)

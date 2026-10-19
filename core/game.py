import sys

import pygame

from core.entities import Character
from core.battle import Battle
from core.enemy_factory import generate_enemy
from core.upgrades import get_random_upgrades
from core.character_factory import build_character
from core.character_factory import get_random_characters

from ui.draw import draw_character_select
from ui.feedback import FeedbackClient
from ui.layout import feedback_layout, game_over_layout, global_feedback_button, menu_buttons, mode_select_buttons, pause_layout, scaled, select_back_button, selection_confirm_buttons
from core.updater import UpdateService, launch_update_helper
from core.version import VERSION


class Game:
    def __init__(self, music=None, display_mode="fullscreen", display_size=None, display_index=0, sound_effects=None, on_audio_change=None):
        from ui.ui_renderer import UIRenderer
        from ui.settings import SettingsScreen
        self.music = music
        self.sound_effects = sound_effects
        self.ui = UIRenderer()
        self.settings_screen = SettingsScreen(
            on_audio_change=on_audio_change or (music.set_audio_levels if music else None),
            audio_levels=music.audio_levels if music else None,
        )
        self.display_mode = display_mode
        self.display_index = display_index
        self.display_size = display_size or pygame.display.get_surface().get_size()
        self.settings_screen.sync(self.display_mode, self.display_size, self.display_index)
        self.display_request = None
        self.exit_requested = False
        self.feedback_client = FeedbackClient()
        self.feedback_kind = None
        self.feedback_title = ""
        self.feedback_message = ""
        self.feedback_severity = None
        self.feedback_focus = "title"
        self.feedback_severity_open = False
        self.feedback_status = ""
        self.feedback_sending = False
        self.feedback_sent_at = None
        self.feedback_return_state = "menu"
        self.version = VERSION
        self.update_info = None
        self.update_message = ""
        self.update_status = "unavailable"
        self.update_service = None
        if sys.platform == "win32" and getattr(sys, "frozen", False):
            self.update_service = UpdateService()
            self.update_status = "checking"
            self.update_service.check_async()
        self.changelog_entries = []
        self.changelog_loading = False
        self.changelog_error = ""

        self.round = 1
        self.state = "menu"
        self.game_mode = "classic"

        # data
        self.lives = 5
        self.character_choices = []
        self.run_character = None
        self.battle_history = []
        self.upgrade_history = []
        self.game_over_battle_scroll = 0
        self.game_over_upgrade_scroll = 0
        self.selected_index = None
        self.hovered_index = None
        self.pending_character_index = None
        self.player = None
        self.enemy = None
        self.battle = None
        self.result = None
        self.result_started_at = None
        self.result_duration_ms = 2200
        self.battle_intro_order = []
        self.battle_intro_index = 0
        self.battle_intro_character = None
        self.battle_intro_started_at = None
        self.battle_intro_duration_ms = 550
        self.click_lock = False
        self.selected_upgrade = None
        self.pause_open = False
        self.pause_started_at = None
        self.pause_return_state = None
        self.settings_from_pause = False
        self.escape_was_down = False

        # upgrades
        self.upgrades = []
        self.upgrade_continuation = "advance"

        # init choices immediately (so select screen works)
        self.character_choices = get_random_characters(5)

    # -------------------------
    # START GAME
    # -------------------------
    def start_game_with_character(self, index):
        raw = self.character_choices[index]

        self.player = build_character(raw, x=150, y=250)
        self.run_character = self.player.name
        self.player.color = (50, 150, 255)

        self.enemy = generate_enemy(self.round)
        self.battle = Battle(self.player, self.enemy, self.sound_effects)
        self._queue_battle_intro()

    def _queue_battle_intro(self):
        self.battle_intro_order = [self.player, self.enemy]
        self._start_battle_intro(0)
        self.state = "battle_intro"

    def _start_battle_intro(self, index):
        self.battle_intro_index = index
        self.battle_intro_character = self.battle_intro_order[index]
        duration = self.sound_effects.play(self.battle_intro_character.intro_sound) if self.sound_effects else None
        if duration is None or duration <= 0:
            duration = 0.55
        self.battle_intro_duration_ms = max(250, round(duration * 1000))
        self.battle_intro_started_at = pygame.time.get_ticks()

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
        self.result_duration_ms = 2200
        self.battle_intro_order = []
        self.battle_intro_index = 0
        self.battle_intro_character = None
        self.battle_intro_started_at = None
        self.upgrade_continuation = "advance"
        self.pending_character_index = None
        self.hovered_index = None
        self.pause_open = False
        self.pause_started_at = None
        if self.sound_effects:
            self.sound_effects.resume()
        self.pause_return_state = None
        self.settings_from_pause = False
        self.run_character = None
        self.battle_history.clear()
        self.upgrade_history.clear()
        self.game_over_battle_scroll = 0
        self.game_over_upgrade_scroll = 0
        self.character_choices = get_random_characters(5)
        self.state = "menu"

    def handle_game_over_scroll(self, amount, position, screen):
        _, _, battles_rect, upgrades_rect = game_over_layout(screen)
        row_height = scaled(screen, 28)
        visible_rows = max(1, (battles_rect.height - scaled(screen, 52)) // row_height)
        if battles_rect.collidepoint(position):
            self.game_over_battle_scroll = max(
                0, min(self.game_over_battle_scroll - amount, len(self.battle_history) - visible_rows)
            )
        elif upgrades_rect.collidepoint(position):
            self.game_over_upgrade_scroll = max(
                0, min(self.game_over_upgrade_scroll - amount, len(self.upgrade_history) - visible_rows)
            )

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
            if self.sound_effects:
                self.sound_effects.pause()

    def _resume_from_pause(self):
        if self.pause_started_at is not None:
            paused_for = pygame.time.get_ticks() - self.pause_started_at
            if self.state == "battle_result" and self.result_started_at is not None:
                self.result_started_at += paused_for
            if self.state == "battle_intro" and self.battle_intro_started_at is not None:
                self.battle_intro_started_at += paused_for
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
        if self.sound_effects:
            self.sound_effects.resume()

    def _open_feedback(self):
        self.feedback_return_state = self.state
        if self.state in ("battle_intro", "battle", "battle_result", "upgrade"):
            self._open_pause()
        self.feedback_kind = None
        self.feedback_title = ""
        self.feedback_message = ""
        self.feedback_severity = None
        self.feedback_status = ""
        self.state = "feedback_type"

    def _begin_update(self):
        if not self.update_info:
            return
        try:
            launch_update_helper(self.update_info)
            self.update_status = "launching"
            self.exit_requested = True
        except Exception as error:
            self.update_message = f"Could not start update: {error}"

    def _poll_update_check(self):
        if self.update_service is None:
            return
        result = self.update_service.take_result()
        if result is None:
            return
        status, payload = result
        if status == "ready":
            self.update_info = payload
            self.update_status = "available" if payload else "current"
        else:
            # A failed check should not prevent an offline game from starting.
            self.update_status = "unavailable"

    def _leave_feedback(self):
        if self.state == "feedback_form":
            pygame.key.stop_text_input()
        self.feedback_kind = None
        self.feedback_title = ""
        self.feedback_message = ""
        self.feedback_severity = None
        self.feedback_focus = "title"
        self.feedback_severity_open = False
        self.feedback_status = ""
        self.feedback_sending = False
        self.feedback_sent_at = None
        self.state = self.feedback_return_state

    def handle_event(self, event):
        if self.state != "feedback_form" or self.feedback_sending:
            return
        if event.type == pygame.TEXTINPUT:
            if self.feedback_focus == "title":
                self.feedback_title = (self.feedback_title + event.text)[:160]
            else:
                self.feedback_message = (self.feedback_message + event.text)[:4000]
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.feedback_focus = "message" if self.feedback_focus == "title" else "title"
            elif event.key == pygame.K_BACKSPACE:
                if self.feedback_focus == "title":
                    self.feedback_title = self.feedback_title[:-1]
                else:
                    self.feedback_message = self.feedback_message[:-1]
            elif event.key == pygame.K_RETURN:
                if self.feedback_focus == "title":
                    self.feedback_focus = "message"
                else:
                    self.feedback_message = (self.feedback_message + "\n")[:4000]
            elif event.key == pygame.K_ESCAPE:
                self._leave_feedback()

    
    # -------------------------
    # UPDATE LOOP (LOGIC ONLY)
    # -------------------------
    def update(self, keys, mouse_pos, mouse_click, screen=None):
        self._poll_update_check()
        escape_down = bool(keys[pygame.K_ESCAPE])
        escape_pressed = escape_down and not self.escape_was_down
        self.escape_was_down = escape_down

        if not mouse_click:
            self.click_lock = False

        if self.state not in ("feedback_type", "feedback_form") and not self.pause_open and mouse_click and not self.click_lock and screen is not None:
            if global_feedback_button(screen).collidepoint(mouse_pos):
                self.click_lock = True
                self._open_feedback()
                return

        # MENU
        if self.state == "menu":
            if mouse_click and not self.click_lock:
                self.click_lock = True

                play_button, settings_button, feedback_button, changelog_button, exit_button = menu_buttons(screen or pygame.display.get_surface())

                if play_button.collidepoint(mouse_pos):
                    if self.update_status == "checking":
                        pass
                    elif self.update_info:
                        self._begin_update()
                    else:
                        self.state = "mode_select"
                elif settings_button.collidepoint(mouse_pos):
                    self.settings_from_pause = False
                    self.state = "settings"
                elif feedback_button.collidepoint(mouse_pos):
                    self._open_feedback()
                elif changelog_button.collidepoint(mouse_pos):
                    self.state = "changelog"
                    self.changelog_entries = []
                    self.changelog_error = ""
                    self.changelog_loading = True
                    self.feedback_client.fetch_changelog()
                elif exit_button.collidepoint(mouse_pos):
                    self.exit_requested = True

            return

        if self.state == "mode_select":
            if escape_pressed:
                self.state = "menu"
                return
            if mouse_click and not self.click_lock and screen is not None:
                self.click_lock = True
                classic_button, endless_button, back_button = mode_select_buttons(screen)
                if classic_button.collidepoint(mouse_pos):
                    self.game_mode = "classic"
                    self.state = "select"
                elif endless_button.collidepoint(mouse_pos):
                    self.game_mode = "endless"
                    self.state = "select"
                elif back_button.collidepoint(mouse_pos):
                    self.state = "menu"
            return

        if self.state in ("feedback_type", "feedback_form"):
            if self.feedback_sending:
                result = self.feedback_client.take_result()
                if result is not None:
                    succeeded, status = result
                    self.feedback_sending = False
                    self.feedback_status = status
                    if succeeded:
                        self.feedback_sent_at = pygame.time.get_ticks()
                return
            if self.feedback_sent_at is not None:
                if pygame.time.get_ticks() - self.feedback_sent_at >= 900:
                    self._leave_feedback()
                return
            if escape_pressed:
                self._leave_feedback()
                return
            if mouse_click and not self.click_lock and screen is not None:
                self.click_lock = True
                _, title_rect, severity_rect, severity_options, content_rect, first, second = feedback_layout(screen)
                if self.state == "feedback_type":
                    if first.collidepoint(mouse_pos):
                        self.feedback_kind = "bug_report"
                        self.feedback_title = ""
                        self.feedback_message = ""
                        self.feedback_severity = None
                        self.feedback_focus = "title"
                        self.feedback_severity_open = False
                        self.feedback_status = ""
                        self.state = "feedback_form"
                        pygame.key.start_text_input()
                    elif second.collidepoint(mouse_pos):
                        self.feedback_kind = "feedback"
                        self.feedback_title = ""
                        self.feedback_message = ""
                        self.feedback_severity = None
                        self.feedback_focus = "title"
                        self.feedback_severity_open = False
                        self.feedback_status = ""
                        self.state = "feedback_form"
                        pygame.key.start_text_input()
                elif self.feedback_severity_open and self.feedback_kind == "bug_report" and any(rect.collidepoint(mouse_pos) for rect in severity_options):
                    index = next(i for i, rect in enumerate(severity_options) if rect.collidepoint(mouse_pos))
                    self.feedback_severity = ("critical", "major", "minor")[index]
                    self.feedback_severity_open = False
                elif self.feedback_kind == "bug_report" and severity_rect.collidepoint(mouse_pos):
                    self.feedback_severity_open = not self.feedback_severity_open
                elif title_rect.collidepoint(mouse_pos):
                    self.feedback_focus = "title"
                    self.feedback_severity_open = False
                elif content_rect.collidepoint(mouse_pos):
                    self.feedback_focus = "message"
                    self.feedback_severity_open = False
                elif first.collidepoint(mouse_pos):
                    if not self.feedback_title.strip():
                        self.feedback_status = "Please enter a title."
                    elif self.feedback_kind == "bug_report" and not self.feedback_severity:
                        self.feedback_status = "Please choose a bug severity."
                    elif not self.feedback_message.strip():
                        self.feedback_status = "Please write a message."
                    else:
                        self.feedback_sending = True
                        self.feedback_status = "Sending..."
                        self.feedback_client.submit(
                            self.feedback_kind,
                            self.feedback_title.strip(),
                            self.feedback_message.strip(),
                            self.feedback_severity,
                        )
                elif second.collidepoint(mouse_pos):
                    self._leave_feedback()
                else:
                    self.feedback_severity_open = False
            return

        if self.state == "changelog":
            result = self.feedback_client.take_changelog_result()
            if result is not None:
                succeeded, payload = result
                self.changelog_loading = False
                if succeeded:
                    self.changelog_entries = payload
                else:
                    self.changelog_error = payload
            if escape_pressed:
                self.state = "menu"
                return
            if mouse_click and not self.click_lock and screen is not None:
                self.click_lock = True
                back = pygame.Rect(scaled(screen, 24), screen.get_height() - scaled(screen, 64), scaled(screen, 150), scaled(screen, 42))
                if back.collidepoint(mouse_pos):
                    self.state = "menu"
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

        if self.state in ("battle_intro", "battle", "battle_result", "upgrade"):
            if escape_pressed:
                if self.pause_open:
                    self._resume_from_pause()
                else:
                    self._open_pause()
                    return

            if self.pause_open:
                if mouse_click and not self.click_lock and screen is not None:
                    self.click_lock = True
                    _, _, _, continue_button, settings_button, feedback_button, menu_button, close_button = pause_layout(screen)
                    if continue_button.collidepoint(mouse_pos) or close_button.collidepoint(mouse_pos):
                        self._resume_from_pause()
                    elif settings_button.collidepoint(mouse_pos):
                        self.pause_return_state = self.state
                        self.settings_from_pause = True
                        self.pause_open = False
                        self.state = "settings"
                    elif feedback_button.collidepoint(mouse_pos):
                        self._open_feedback()
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
        if self.state == "battle_intro":
            if pygame.time.get_ticks() - self.battle_intro_started_at >= self.battle_intro_duration_ms:
                if self.battle_intro_index + 1 < len(self.battle_intro_order):
                    self._start_battle_intro(self.battle_intro_index + 1)
                else:
                    now = pygame.time.get_ticks()
                    self.battle.player_last_attack = now
                    self.battle.enemy_last_attack = now
                    self.state = "battle"
            return

        if self.state == "battle":
            if not self.battle.finished:
                self.battle.update()
            else:
                self.result = self.battle.winner

                if self.result == "enemy":
                    self.lives -= 1
                    print (f"LIFE LOST! Lives remaining: {self.lives}")

                self.battle_history.append({
                    "round": self.round,
                    "opponent": getattr(self.enemy, "name", "Unknown opponent"),
                    "result": "Victory" if self.result == "player" else "Defeat",
                    "player_hp": max(0, self.player.hp),
                    "player_max_hp": self.player.max_hp,
                    "lives": self.lives,
                })

                self.result_started_at = pygame.time.get_ticks()
                player_result_sound = self.player.win_sound if self.result == "player" else self.player.lose_sound
                sound_length = self.sound_effects.play(player_result_sound) if self.sound_effects else None
                self.result_duration_ms = max(
                    2200,
                    round(sound_length * 1000) if sound_length is not None else 0,
                )
                self.state = "battle_result"
            return

        if self.state == "battle_result":
            if self.pause_open:
                return
            if pygame.time.get_ticks() - self.result_started_at >= self.result_duration_ms:
                if self.game_mode == "classic" and self.result == "player" and self.round >= 20:
                    self.state = "game_win"
                elif self.lives <= 0:
                    self.state = "game_over"
                elif self.game_mode == "classic" and self.result != "player":
                    self.upgrade_continuation = "retry_level"
                    self.start_upgrade()
                    self.state = "upgrade"
                else:
                    self.upgrade_continuation = "advance_level"
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
                        self.upgrade_history.append({"round": self.round, "name": upg.get("name", "Upgrade")})

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

                        if self.upgrade_continuation == "retry_level":
                            self.upgrade_continuation = "advance_level"
                            self._retry_current_level()
                        else:
                            self.state = "next"
                        break

            return

        # NEXT ROUND
        if self.state == "next":
            self.round += 1
            self.player.hp = self.player.max_hp
            self.enemy = generate_enemy(self.round)
            self.battle = Battle(self.player, self.enemy, self.sound_effects)
            self._queue_battle_intro()
            return

        if self.state == "game_over":
            if mouse_click and not self.click_lock and screen is not None:
                self.click_lock = True
                retry_button, menu_button, _, _ = game_over_layout(screen)
                if retry_button.collidepoint(mouse_pos):
                    self.reset_run()
                    self.state = "mode_select"
                elif menu_button.collidepoint(mouse_pos):
                    self.reset_run()
            return

        if self.state == "game_win":
            if mouse_click and not self.click_lock and screen is not None:
                self.click_lock = True
                play_again_button, menu_button, _, _ = game_over_layout(screen)
                if play_again_button.collidepoint(mouse_pos):
                    self.reset_run()
                    self.state = "mode_select"
                elif menu_button.collidepoint(mouse_pos):
                    self.reset_run()
            return

    def _retry_current_level(self):
        """Set up another attempt at the current Classic level after a loss."""
        self.player.hp = self.player.max_hp
        self.enemy = generate_enemy(self.round)
        self.battle = Battle(self.player, self.enemy, self.sound_effects)
        self.result = None
        self.result_started_at = None
        self._queue_battle_intro()

    # -------------------------
    # DRAW LOOP (RENDER ONLY)
    # -------------------------
    def draw(self, screen, mouse_pos):
        self.ui.draw(self, screen, mouse_pos)

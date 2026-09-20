import pygame
from ui.draw import get_sprite

class Battle:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

        # individual timers
        self.player_last_attack = 0
        self.enemy_last_attack = 0

        self.finished = False
        self.winner = None

    def update(self):
        if self.finished:
            return

        now = pygame.time.get_ticks()

        # convert attack speed → delay (ms)
        player_delay = 1000 / self.player.attack_speed
        enemy_delay = 1000 / self.enemy.attack_speed

        # PLAYER ATTACK
        if now - self.player_last_attack > player_delay:
            if self.player.is_alive() and self.enemy.is_alive():
                self.player.attack(self.enemy)
            self.player_last_attack = now

        # ENEMY ATTACK
        if now - self.enemy_last_attack > enemy_delay:
            if self.enemy.is_alive() and self.player.is_alive():
                self.enemy.attack(self.player)
            self.enemy_last_attack = now

        # 🏁 END CHECK
        if not self.player.is_alive() or not self.enemy.is_alive():
            self.finished = True
            self.winner = "player" if self.player.is_alive() else "enemy"

    def draw(self, screen):
        self.draw_character(screen, self.player)
        self.draw_character(screen, self.enemy)

    def draw_character(self, screen, char):
        offset = 0
        if char.is_alive():
            offset = (pygame.time.get_ticks() // 200) % 4

        y = char.y - offset

        if char.sprite_name:
            try:
                img = get_sprite(char.sprite_name)
                screen.blit(img, (char.x, y))
            except Exception as e:
                print("SPRITE ERROR:", char.sprite_name, e)
                pygame.draw.rect(screen, char.color, (char.x, char.y, 80, 80))
        else:
            pygame.draw.rect(screen, char.color, (char.x, char.y, 80, 80))

        # HP BAR
        hp_ratio = max(0, char.hp / char.max_hp)
        pygame.draw.rect(screen, (200, 0, 0), (char.x, char.y - 10, 80, 5))
        pygame.draw.rect(screen, (0, 200, 0), (char.x, char.y - 10, 80 * hp_ratio, 5))
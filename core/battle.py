import pygame



class Battle:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

        self.attack_delay = 800
        self.last_attack_time = 0

        self.finished = False
        self.winner = None

    def update(self):
        if self.finished:
            return

        now = pygame.time.get_ticks()

        if now - self.last_attack_time > self.attack_delay:
            if self.player.is_alive() and self.enemy.is_alive():
                self.player.attack(self.enemy)
                self.enemy.attack(self.player)

            self.last_attack_time = now

        # 🏁 check end condition
        if not self.player.is_alive() or not self.enemy.is_alive():
            self.finished = True
            self.winner = "player" if self.player.is_alive() else "enemy"

    def draw(self, screen):
        self.draw_character(screen, self.player)
        self.draw_character(screen, self.enemy)

    def draw_character(self, screen, char):
        offset = 0

        if char.is_alive():
            offset = (pygame.time.get_ticks() // 200) % 4 #small animation effect for Alice

        y = char.y - offset


        if char.sprite_name:
            img = pygame.image.load(f"assets/sprites/{char.sprite_name}").convert_alpha()
            screen.blit(img, (char.x, y))
        else:
            pygame.draw.rect(screen, char.color, (char.x, char.y, 80, 80))

        hp_ratio = max(0, char.hp / char.max_hp)
        pygame.draw.rect(screen, (200, 0, 0), (char.x, char.y - 10, 80, 5))
        pygame.draw.rect(screen, (0, 200, 0), (char.x, char.y - 10, 80 * hp_ratio, 5))
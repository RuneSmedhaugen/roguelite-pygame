import pygame


class Button:
    def __init__(self, rect, text, font,
                 color_idle=(60, 60, 60),
                 color_hover=(120, 120, 120),
                 text_color=(0, 0, 0)):

        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font

        self.color_idle = color_idle
        self.color_hover = color_hover
        self.text_color = text_color

        self.hovered = False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        color = self.color_hover if self.hovered else self.color_idle
        pygame.draw.rect(screen, color, self.rect, border_radius=10)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, mouse_pos, mouse_click):
        return self.hovered and mouse_click
import pygame

class Fade:
    def __init__(self, screen, width, height, fade_speed=5):
        self.screen = screen
        self.width = width
        self.height = height
        self.fade_speed = fade_speed
        self.alpha = 0
        self.fading = False
        self.fade_direction = None  # 'out' or 'in'
        self.surface = pygame.Surface((width, height))
        self.surface.fill((0, 0, 0))

    def start_fade_out(self):
        """Start fading out (screen becomes black)"""
        self.fading = True
        self.fade_direction = 'out'
        self.alpha = 0

    def start_fade_in(self):
        """Start fading in (screen becomes transparent)"""
        self.fading = True
        self.fade_direction = 'in'
        self.alpha = 255

    def update(self):
        """Update fade effect"""
        if self.fading:
            if self.fade_direction == 'out':
                # Fade to black
                self.alpha += self.fade_speed
                if self.alpha >= 255:
                    self.alpha = 255
                    self.fading = False
                    return True  # Faded out completely
            elif self.fade_direction == 'in':
                # Fade from black
                self.alpha -= self.fade_speed
                if self.alpha <= 0:
                    self.alpha = 0
                    self.fading = False
                    return True  # Faded in completely
        return False

    def draw(self):
        """Draw the fade overlay"""
        if self.fading:
            self.surface.set_alpha(self.alpha)
            self.screen.blit(self.surface, (0, 0))
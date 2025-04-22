import pygame
from settings import FONT_PATH, FONT_SIZE


class InputBox:
    def __init__(self, x, y, width, height, text='', placeholder='', font_size=FONT_SIZE, password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.original_width = width  # Store the original width
        self.color_inactive = pygame.Color('black')  # Border color when inactive
        self.color_active = pygame.Color('black')  # Border color when active
        self.color = self.color_inactive
        self.text = text
        self.placeholder = placeholder
        self.font = pygame.font.Font(FONT_PATH, 40)
        self.txt_surface = self.font.render(text, True, pygame.Color('white'))
        self.active = False
        self.password = password
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_speed = 500  # Milliseconds
        self.text_offset = 0  # For scrolling text horizontally
        self.padding = 10  # Padding inside the input box

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input box
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable
                self.active = True
                self.color = self.color_active
            else:
                self.active = False
                self.color = self.color_inactive

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                    # Reset text offset when text is deleted
                    self.adjust_text_offset()
                elif event.key == pygame.K_RETURN:
                    return True  # Signal that Enter was pressed
                else:
                    # Add character to text if it's printable
                    if event.unicode.isprintable():
                        self.text += event.unicode
                        self.adjust_text_offset()  # Adjust offset after adding text

                # Re-render the text
                displayed_text = '*' * len(self.text) if self.password else self.text
                self.txt_surface = self.font.render(displayed_text, True, pygame.Color('white'))

        return False  # No special action needed

    def adjust_text_offset(self):
        # Calculate if text width exceeds visible area
        displayed_text = '*' * len(self.text) if self.password else self.text
        text_width = self.font.render(displayed_text, True, pygame.Color('white')).get_width()

        max_visible_width = self.rect.width - (2 * self.padding)

        # If text exceeds visible area, adjust offset to show the end of the text
        if text_width > max_visible_width:
            self.text_offset = min(0, max_visible_width - text_width)
        else:
            self.text_offset = 0

    def update(self):
        # Do NOT resize the box - keep it at the original width
        self.rect.w = self.original_width

        # Handle cursor blinking
        self.cursor_timer += pygame.time.get_ticks() % 1000
        if self.cursor_timer >= self.cursor_blink_speed:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, screen):
        # Calculate vertical center for text
        text_y = self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2

        # Create a surface for clipping the text
        clip_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width - 2, self.rect.height - 2)
        clip_surface = pygame.Surface((clip_rect.width, clip_rect.height), pygame.SRCALPHA)
        clip_surface.fill((255, 255, 255, 0))  # Transparent background

        # Render placeholder if empty and not active
        if not self.text and not self.active:
            placeholder_surface = self.font.render(self.placeholder, True, pygame.Color('grey'))
            clip_surface.blit(placeholder_surface,
                              (self.padding, (clip_rect.height - placeholder_surface.get_height()) // 2))
        else:
            # Render the text
            displayed_text = '*' * len(self.text) if self.password else self.text
            self.txt_surface = self.font.render(displayed_text, True, pygame.Color('black'))
            clip_surface.blit(self.txt_surface, (self.padding + self.text_offset,
                                                 (clip_rect.height - self.txt_surface.get_height()) // 2))

        # Draw cursor when active
        if self.active and self.cursor_visible:
            cursor_pos_x = self.padding + self.text_offset + self.txt_surface.get_width()
            if cursor_pos_x < self.rect.width - self.padding:  # Only draw cursor if it's in the visible area
                cursor_y_offset = (clip_rect.height - self.txt_surface.get_height()) // 2
                pygame.draw.line(
                    clip_surface,
                    pygame.Color('black'),
                    (cursor_pos_x, cursor_y_offset),
                    (cursor_pos_x, cursor_y_offset + self.txt_surface.get_height()),
                    2
                )

        # Blit the clipped surface onto the screen
        screen.blit(clip_surface, (self.rect.x + 1, self.rect.y + 1))

        # Draw the rectangle border
        pygame.draw.rect(screen, self.color, self.rect, 2)
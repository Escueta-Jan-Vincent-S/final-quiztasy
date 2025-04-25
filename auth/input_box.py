import pygame
from settings import FONT_PATH, FONT_SIZE


class InputBox:
    def __init__(self, x, y, width, height, text='', placeholder='', font_size=FONT_SIZE, password=False,
                 align_top_left=False, multiline=False):
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
        self.cursor_timer = pygame.time.get_ticks()
        self.cursor_blink_speed = 500  # Milliseconds
        self.text_offset = 0  # For scrolling text horizontally
        self.padding = 10  # Padding inside the input box
        self.align_top_left = align_top_left  # New parameter for text alignment
        self.multiline = multiline  # Support for multiline text (for questions)
        self.lines = []  # For multiline text
        self.max_chars_per_line = 0  # Will be calculated based on width

        # Calculate max chars per line based on average character width
        self.calculate_max_chars_per_line()

        # Initialize lines if multiline is enabled
        if multiline and text:
            self.format_multiline_text()

    def calculate_max_chars_per_line(self):
        """Calculate approximately how many characters fit in one line based on width."""
        # Use 'm' as a reference character (average width)
        test_char = 'm'
        char_width = self.font.render(test_char, True, pygame.Color('white')).get_width()
        available_width = self.rect.width - (2 * self.padding)
        self.max_chars_per_line = max(1, int(available_width / char_width))

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
                modified = False
                if event.key == pygame.K_BACKSPACE:
                    if self.text:
                        self.text = self.text[:-1]
                        modified = True
                elif event.key == pygame.K_RETURN:
                    if self.multiline:
                        self.text += '\n'  # Add newline for multiline inputs
                        modified = True
                    else:
                        return True  # Signal that Enter was pressed
                else:
                    # Add character to text if it's printable
                    if event.unicode.isprintable():
                        self.text += event.unicode
                        modified = True

                # Handle text formatting after modifications
                if modified:
                    if self.multiline:
                        self.format_multiline_text()
                    else:
                        self.adjust_text_offset()
                        # Re-render the text for single line inputs
                        displayed_text = '*' * len(self.text) if self.password else self.text
                        self.txt_surface = self.font.render(displayed_text, True, pygame.Color('white'))

        return False  # No special action needed

    def format_multiline_text(self):
        """Split text into multiple lines that fit within the box width."""
        available_width = self.rect.width - (2 * self.padding)

        # Start with empty lines
        self.lines = []

        if not self.text:
            return

        # Split text by newlines first
        paragraphs = self.text.split('\n')

        for paragraph in paragraphs:
            if not paragraph:  # Empty paragraph becomes a blank line
                self.lines.append("")
                continue

            # First try to break by words
            words = paragraph.split()

            if words:
                current_line = ""

                for word in words:
                    # Check if adding this word would exceed the width
                    test_line = current_line + (" " + word if current_line else word)
                    test_surface = self.font.render(test_line, True, pygame.Color('white'))

                    if test_surface.get_width() <= available_width:
                        current_line = test_line
                    else:
                        # Word doesn't fit, add current line and start a new one
                        if current_line:
                            self.lines.append(current_line)

                        # Check if the word itself is too long and needs breaking
                        if self.font.render(word, True, pygame.Color('white')).get_width() > available_width:
                            # Break the word into chunks that fit
                            remaining_word = word
                            while remaining_word:
                                char_count = 1
                                while char_count <= len(remaining_word):
                                    chunk = remaining_word[:char_count]
                                    if self.font.render(chunk, True,
                                                        pygame.Color('white')).get_width() > available_width:
                                        # Use previous valid chunk
                                        if char_count > 1:
                                            char_count -= 1
                                        break
                                    char_count += 1

                                # Add the chunk that fits
                                if char_count > 0:
                                    self.lines.append(remaining_word[:char_count])
                                    remaining_word = remaining_word[char_count:]
                                else:
                                    # Failsafe - add at least one character if nothing fits
                                    self.lines.append(remaining_word[:1])
                                    remaining_word = remaining_word[1:]
                        else:
                            # Word fits on its own line
                            current_line = word

                # Add the last line if there's anything left
                if current_line:
                    self.lines.append(current_line)
            else:
                # Handle long continuous text (no spaces)
                remaining_text = paragraph
                while remaining_text:
                    # Try to fit as many characters as possible
                    char_count = 1
                    while char_count <= len(remaining_text):
                        chunk = remaining_text[:char_count]
                        if self.font.render(chunk, True, pygame.Color('white')).get_width() > available_width:
                            # Use previous valid chunk
                            if char_count > 1:
                                char_count -= 1
                            break
                        char_count += 1

                    # Add the chunk that fits
                    if char_count > 0:
                        self.lines.append(remaining_text[:char_count])
                        remaining_text = remaining_text[char_count:]
                    else:
                        # Failsafe - add at least one character if nothing else fits
                        self.lines.append(remaining_text[:1])
                        remaining_text = remaining_text[1:]

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
        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_timer >= self.cursor_blink_speed:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = current_time

    def draw(self, screen):
        if self.multiline:
            self.draw_multiline(screen)
        else:
            self.draw_single_line(screen)

    def draw_multiline(self, screen):
        # Create a surface for clipping the text
        clip_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width - 2, self.rect.height - 2)
        clip_surface = pygame.Surface((clip_rect.width, clip_rect.height), pygame.SRCALPHA)
        clip_surface.fill((255, 255, 255, 0))  # Transparent background

        # Render placeholder if empty and not active
        if not self.text and not self.active:
            placeholder_surface = self.font.render(self.placeholder, True, pygame.Color('grey'))
            clip_surface.blit(placeholder_surface,
                              (self.padding, self.padding if self.align_top_left else
                              (clip_rect.height - placeholder_surface.get_height()) // 2))
        else:
            # Format text if not already done
            if not self.lines:
                self.format_multiline_text()

            # Render each line
            y_offset = self.padding if self.align_top_left else (
                    (clip_rect.height - (len(self.lines) * self.font.get_height())) // 2
            )

            for i, line in enumerate(self.lines):
                line_surface = self.font.render(line, True, pygame.Color('black'))
                clip_surface.blit(line_surface, (self.padding, y_offset + i * self.font.get_height()))

            # Draw cursor at the end of the last line if active
            if self.active and self.cursor_visible:
                if self.lines:
                    # Get last line to position cursor
                    last_line = self.lines[-1]
                    last_line_surface = self.font.render(last_line, True, pygame.Color('black'))
                    cursor_x = self.padding + last_line_surface.get_width()
                    cursor_y = y_offset + (len(self.lines) - 1) * self.font.get_height()
                else:
                    # If no lines, cursor at beginning
                    cursor_x = self.padding
                    cursor_y = y_offset

                pygame.draw.line(
                    clip_surface,
                    pygame.Color('black'),
                    (cursor_x, cursor_y),
                    (cursor_x, cursor_y + self.font.get_height()),
                    2
                )

        # Blit the clipped surface onto the screen
        screen.blit(clip_surface, (self.rect.x + 1, self.rect.y + 1))

        # Draw the rectangle border
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def draw_single_line(self, screen):
        # For single line inputs - original implementation
        # Calculate vertical center or top alignment for text
        if self.align_top_left:
            text_y = self.rect.y + self.padding
        else:
            text_y = self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2

        # Create a surface for clipping the text
        clip_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width - 2, self.rect.height - 2)
        clip_surface = pygame.Surface((clip_rect.width, clip_rect.height), pygame.SRCALPHA)
        clip_surface.fill((255, 255, 255, 0))  # Transparent background

        # Render placeholder if empty and not active
        if not self.text and not self.active:
            placeholder_surface = self.font.render(self.placeholder, True, pygame.Color('grey'))
            placeholder_y = self.padding if self.align_top_left else (
                    (clip_rect.height - placeholder_surface.get_height()) // 2
            )
            clip_surface.blit(placeholder_surface, (self.padding, placeholder_y))
        else:
            # Render the text
            displayed_text = '*' * len(self.text) if self.password else self.text
            self.txt_surface = self.font.render(displayed_text, True, pygame.Color('black'))
            text_y_offset = self.padding if self.align_top_left else (
                    (clip_rect.height - self.txt_surface.get_height()) // 2
            )
            clip_surface.blit(self.txt_surface, (self.padding + self.text_offset, text_y_offset))

        # Draw cursor when active
        if self.active and self.cursor_visible:
            cursor_pos_x = self.padding + self.text_offset + self.txt_surface.get_width()
            if cursor_pos_x < self.rect.width - self.padding:  # Only draw cursor if it's in the visible area
                cursor_y_offset = self.padding if self.align_top_left else (
                        (clip_rect.height - self.txt_surface.get_height()) // 2
                )
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
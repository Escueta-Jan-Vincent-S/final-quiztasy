import pygame
import os
from ui.button import Button
from ui.back_button import BackButton
from auth.input_box import InputBox
from settings import FONT_PATH, FONT_SIZE

class CustomUI:
    def __init__(self, screen, audio_manager, script_dir, scale=0.5, custom_mode=None):
        self.custom_mode = custom_mode
        self.screen = screen
        self.audio_manager = audio_manager
        self.visible = False
        self.scale = scale
        self.script_dir = script_dir

        # Font for slots
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZE)
        self.small_font = pygame.font.Font(FONT_PATH, FONT_SIZE // 2)

        # Save slot config
        self.slot_width = 800
        self.slot_height = 80
        self.slot_spacing = 10
        self.border_thickness = 2
        self.slot_border_color = (127, 127, 127)  # Gray border color
        self.slot_background_color = (50, 50, 50)  # Dark background for slots
        self.selected_slot_color = (60, 60, 60)  # Slightly lighter when selected
        self.text_color = (255, 255, 255)  # White text

        # Area border color (changed to transparent gray)
        self.area_background_color = (80, 80, 80, 160)  # Gray with transparency

        # Scrolling functionality
        self.scroll_y = 0
        self.max_scroll = 0
        self.scroll_speed = 20
        self.visible_area = pygame.Rect(560, 200, self.slot_width, 600)

        # Status message for validation (similar to login screen)
        self.status_message = ""
        self.status_color = pygame.Color('white')
        self.status_timer = 0  # Timer to clear the message after some time

        # Create UI elements
        self.setup_ui_elements()

    def setup_ui_elements(self):
        """Initialize all UI elements"""
        # Create Button
        create_btn_path = os.path.join(self.script_dir, "assets", "images", "buttons", "game modes", "custom", "createquestion_btn_img.png")
        create_btn_hover_path = os.path.join(self.script_dir, "assets", "images", "buttons", "game modes", "custom", "createquestion_btn_hover.png")

        self.create_button = Button(960, 875, create_btn_path, create_btn_hover_path, None, lambda: self.custom_mode.create_question(), scale=0.5, audio_manager=self.audio_manager)
        # Back Button
        self.back_button = BackButton(self.screen, self.script_dir, lambda: self.custom_mode.go_back(), audio_manager=self.audio_manager, position=(100, 100), scale=0.25)

        # Load input border
        input_border_path = os.path.join(self.script_dir, "assets", "images", "buttons", "game modes", "custom", "input_border.png")
        self.input_border = pygame.image.load(input_border_path).convert_alpha()
        self.input_border = pygame.transform.scale(self.input_border, (int(self.input_border.get_width() * 0.7), int(self.input_border.get_height() * 0.7)))
        self.input_border_rect = self.input_border.get_rect(center=(960, 500))

        # Input boxes for question and answer with updated parameters
        self.question_input = InputBox(310, 290, 1300, 260, placeholder="Enter your question here...", align_top_left=True, multiline=True)
        self.answer_input = InputBox(310, 700, 1300, 120, placeholder="Enter the answer here...", align_top_left=True)

        # Next and Done buttons
        next_btn_path = os.path.join(self.script_dir, "assets", "images", "buttons", "game modes", "custom", "next_btn_img.png")
        next_btn_hover_path = os.path.join(self.script_dir, "assets", "images", "buttons", "game modes", "custom", "next_btn_hover.png")
        done_btn_path = os.path.join(self.script_dir, "assets", "images", "buttons", "game modes", "custom", "done_btn_img.png")
        done_btn_hover_path = os.path.join(self.script_dir, "assets", "images", "buttons", "game modes", "custom", "done_btn_hover.png")

        self.next_button = Button(700, 950, next_btn_path, next_btn_hover_path, None, lambda: self.custom_mode.next_question(), scale=0.5, audio_manager=self.audio_manager)
        self.done_button = Button(1200, 950, done_btn_path, done_btn_hover_path, None, lambda: self.custom_mode.done_creating(), scale=0.5, audio_manager=self.audio_manager)

        # Load X button for removing slots
        x_button_path = os.path.join(self.script_dir, "assets", "images", "buttons", "game modes", "custom", "x_button.png")
        x_button_hover_path = os.path.join(self.script_dir, "assets", "images", "buttons", "game modes", "custom", "x_button_hover.png")

        # If the exact files don't exist, you may need to use placeholder images initially
        try:
            self.x_button_img = pygame.image.load(x_button_path).convert_alpha()
            self.x_button_hover_img = pygame.image.load(x_button_hover_path).convert_alpha()
        except:
            # Create a fallback X button if images don't exist
            print("X button images not found, creating fallback buttons")
            # Create a red X button as fallback
            self.x_button_img = self.create_x_button((255, 0, 0))
            self.x_button_hover_img = self.create_x_button((255, 100, 100))

        # Scale the X button images
        button_size = 30
        self.x_button_img = pygame.transform.scale(self.x_button_img, (button_size, button_size))
        self.x_button_hover_img = pygame.transform.scale(self.x_button_hover_img, (button_size, button_size))

        # Track which X button is being hovered
        self.hovered_x_button = None

    def create_x_button(self, color):
        """Create a simple X button surface"""
        size = 30
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Draw X
        thickness = 4
        pygame.draw.line(surface, color, (5, 5), (size - 5, size - 5), thickness)
        pygame.draw.line(surface, color, (size - 5, 5), (5, size - 5), thickness)

        # Draw circle border
        pygame.draw.circle(surface, color, (size // 2, size // 2), size // 2 - 1, 2)

        return surface

    def update_max_scroll(self, save_slots):
        """Update the maximum scrolling value based on content height."""
        total_height = len(save_slots) * (self.slot_height + self.slot_spacing)
        visible_height = self.visible_area.height
        self.max_scroll = max(0, total_height - visible_height)

    def update(self, event, creating_question, save_slots, selected_slot):
        """Update UI elements and handle events."""
        if not self.visible:
            return None

        self.back_button.update(event)

        result = None

        if creating_question:
            # Update input boxes and buttons in question creation mode
            self.question_input.handle_event(event)
            self.answer_input.handle_event(event)
            self.next_button.update(event)
            self.done_button.update(event)

            # Clear status message after 3 seconds
            if self.status_message and pygame.time.get_ticks() - self.status_timer > 3000:
                self.status_message = ""
        else:
            # Update regular slot view
            self.create_button.update(event)

            # Handle mouse wheel scrolling
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_y -= event.y * self.scroll_speed
                # Clamp scrolling to valid range
                self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

            # Handle clicks on slots and X buttons
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Check if click is within visible area
                if self.visible_area.collidepoint(mouse_x, mouse_y):
                    # Calculate which slot was clicked
                    adjusted_y = mouse_y - self.visible_area.top + self.scroll_y
                    slot_index = int(adjusted_y / (self.slot_height + self.slot_spacing))

                    if 0 <= slot_index < len(save_slots):
                        # Check if X button area was clicked
                        slot_y = self.visible_area.top + slot_index * (
                                self.slot_height + self.slot_spacing) - self.scroll_y
                        slot_rect = pygame.Rect(self.visible_area.left, slot_y, self.slot_width, self.slot_height)
                        x_button_rect = pygame.Rect(
                            slot_rect.right - 40,  # Position 40px from right edge
                            slot_rect.centery - 15,  # Centered vertically
                            30, 30  # Size of the button
                        )

                        if x_button_rect.collidepoint(mouse_x, mouse_y):
                            # X button clicked, remove this slot
                            result = {"action": "delete_slot", "index": slot_index}
                        else:
                            # Normal slot selection
                            print(f"Selected slot: {save_slots[slot_index]}")
                            result = {"action": "select_slot", "index": slot_index}

            # Clear status message after 3 seconds
            if self.status_message and pygame.time.get_ticks() - self.status_timer > 3000:
                self.status_message = ""

        return result

    def draw(self, creating_question, save_slots, selected_slot, current_questions):
        """Draw all UI elements."""
        if not self.visible:
            return

        # Draw back button
        self.back_button.draw()

        if creating_question:
            # Draw the question creation interface
            # Draw the background border
            self.screen.blit(self.input_border, self.input_border_rect)

            # Draw input fields
            self.question_input.update()  # Make sure to update input boxes
            self.answer_input.update()
            self.question_input.draw(self.screen)
            self.answer_input.draw(self.screen)

            # Draw buttons
            self.next_button.draw(self.screen)
            self.done_button.draw(self.screen)

            # Draw question count
            count_text = f"Questions added: {len(current_questions)}"
            count_surface = self.small_font.render(count_text, True, self.text_color)
            self.screen.blit(count_surface, (self.question_input.rect.x, 260))

            # Draw status message if any
            if self.status_message:
                status_surf = self.font.render(self.status_message, True, self.status_color)
                status_x = 960 - status_surf.get_width() // 2  # Center horizontally
                status_y = 850  # Position above the buttons
                self.screen.blit(status_surf, (status_x, status_y))
        else:
            # Draw slots view
            # Create transparent surface for the gray background area
            bg_surface = pygame.Surface((self.visible_area.width, self.visible_area.height), pygame.SRCALPHA)
            bg_surface.fill(self.area_background_color)  # This will use the alpha value
            self.screen.blit(bg_surface, self.visible_area.topleft)

            # Draw the border separately
            pygame.draw.rect(self.screen, self.slot_border_color, self.visible_area, self.border_thickness)

            # Create a clipping rect for the visible area
            original_clip = self.screen.get_clip()
            self.screen.set_clip(self.visible_area)

            # Reset hovered X button state
            self.hovered_x_button = None
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Draw all slots
            for i, slot_text in enumerate(save_slots):
                # Calculate position with scrolling offset
                slot_y = self.visible_area.top + i * (self.slot_height + self.slot_spacing) - self.scroll_y
                slot_rect = pygame.Rect(self.visible_area.left, slot_y, self.slot_width, self.slot_height)

                # Skip slots that are outside the visible area
                if slot_rect.bottom < self.visible_area.top or slot_rect.top > self.visible_area.bottom:
                    continue

                # Draw slot background
                bg_color = self.selected_slot_color if i == selected_slot else self.slot_background_color
                pygame.draw.rect(self.screen, bg_color, slot_rect)
                pygame.draw.rect(self.screen, self.slot_border_color, slot_rect, self.border_thickness)

                # Draw slot text
                text_surface = self.font.render(slot_text, True, self.text_color)
                text_rect = text_surface.get_rect(midleft=(slot_rect.left + 20, slot_rect.centery))
                self.screen.blit(text_surface, text_rect)

                # Add X button for removing slot
                x_button_rect = pygame.Rect(
                    slot_rect.right - 40,  # Position 40px from right edge
                    slot_rect.centery - 15,  # Centered vertically
                    30, 30  # Size of the button
                )

                # Check if mouse is hovering over this X button
                if x_button_rect.collidepoint(mouse_x, mouse_y):
                    self.hovered_x_button = i
                    x_img = self.x_button_hover_img
                else:
                    x_img = self.x_button_img

                # Draw the X button
                self.screen.blit(x_img, x_button_rect)

            # Reset clipping rect
            self.screen.set_clip(original_clip)

            # Draw scrollbar if needed
            if self.max_scroll > 0:
                scrollbar_height = max(30, self.visible_area.height * (
                        self.visible_area.height / (self.max_scroll + self.visible_area.height)))
                scrollbar_y = self.visible_area.top + (self.scroll_y / self.max_scroll) * (
                        self.visible_area.height - scrollbar_height)
                scrollbar_rect = pygame.Rect(self.visible_area.right + 10, scrollbar_y, 10, scrollbar_height)
                pygame.draw.rect(self.screen, self.slot_border_color, scrollbar_rect)

            # Draw create button
            self.create_button.draw(self.screen)

            # Draw status message if any
            if self.status_message:
                status_surf = self.font.render(self.status_message, True, self.status_color)
                status_x = 960 - status_surf.get_width() // 2  # Center horizontally
                status_y = 850  # Position above the create button
                self.screen.blit(status_surf, (status_x, status_y))

    def set_status(self, message, color=pygame.Color('white')):
        """Set status message with given color"""
        self.status_message = message
        self.status_color = color
        self.status_timer = pygame.time.get_ticks()

    def get_input_values(self):
        """Return the current values of input boxes"""
        return {
            "question": self.question_input.text.strip(),
            "answer": self.answer_input.text.strip()
        }

    def reset_inputs(self):
        """Clear input box values"""
        self.question_input.text = ""
        self.answer_input.text = ""

    def show(self):
        """Show the UI"""
        self.visible = True
        self.scroll_y = 0  # Reset scroll position

    def hide(self):
        """Hide the UI"""
        self.visible = False
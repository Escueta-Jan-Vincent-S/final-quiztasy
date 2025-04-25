import pygame
import os
from ui.button import Button
from ui.back_button import BackButton
from settings import FONT_PATH, FONT_SIZE

class CustomMode:
    def __init__(self, screen, audio_manager, script_dir, scale=0.5, game_instance=None):
        self.game_instance = game_instance
        self.screen = screen
        self.audio_manager = audio_manager
        self.visible = False
        self.scale = scale

        # Font for slots
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZE)

        # Save slot config
        self.slot_width = 800
        self.slot_height = 80
        self.slot_spacing = 10
        self.border_thickness = 2
        self.slot_border_color = (100, 255, 100)  # Green border color
        self.slot_background_color = (30, 30, 30)  # Dark background for slots
        self.selected_slot_color = (60, 60, 60)  # Slightly lighter when selected
        self.text_color = (255, 255, 255)  # White text

        # Scrolling functionality
        self.scroll_y = 0
        self.max_scroll = 0
        self.scroll_speed = 20
        self.visible_area = pygame.Rect(560, 200, self.slot_width, 600)

        # Initial save slots (can be loaded from storage later)
        self.save_slots = [f"Question Slot {i + 1}" for i in range(10)]
        self.selected_slot = None

        # Create Button
        create_btn_path = os.path.join(script_dir, "assets", "images", "buttons", "game modes", "custom","createquestion_btn_img.png")
        create_btn_hover_path = os.path.join(script_dir, "assets", "images", "buttons", "game modes", "custom", "createquestion_btn_hover.png")

        self.create_button = Button(
            960, 850, create_btn_path, create_btn_hover_path, None,
            self.create_question, scale=0.5, audio_manager=self.audio_manager
        )

        # Back Button
        self.back_button = BackButton(self.screen, script_dir, self.go_back, audio_manager=self.audio_manager,
                                      position=(100, 100), scale=0.25)

        # Calculate maximum scroll value
        self.update_max_scroll()

    def update_max_scroll(self):
        """Update the maximum scrolling value based on content height."""
        total_height = len(self.save_slots) * (self.slot_height + self.slot_spacing)
        visible_height = self.visible_area.height
        self.max_scroll = max(0, total_height - visible_height)

    def create_question(self):
        """Handle create button click."""
        print("Create Question Clicked")
        # Add new save slot
        new_slot_index = len(self.save_slots) + 1
        self.save_slots.append(f"Question Slot {new_slot_index}")
        self.update_max_scroll()

    def remove_slot(self, slot_index):
        """Remove a save slot."""
        if 0 <= slot_index < len(self.save_slots):
            print(f"Removing slot: {self.save_slots[slot_index]}")
            self.save_slots.pop(slot_index)
            if self.selected_slot == slot_index:
                self.selected_slot = None
            elif self.selected_slot > slot_index:
                self.selected_slot -= 1
            self.update_max_scroll()

    def go_back(self):
        """Handle back button click."""
        print("Back button clicked!")
        self.hide()
        # Return to game modes
        if self.game_instance and hasattr(self.game_instance, 'game_modes'):
            self.game_instance.game_modes.show()

            if hasattr(self.game_instance, 'main_menu'):
                self.game_instance.main_menu.show_game_logo = False

    def update(self, event):
        """Update UI elements and handle events."""
        if not self.visible:
            return

        self.back_button.update(event)
        self.create_button.update(event)

        # Handle mouse wheel scrolling
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y -= event.y * self.scroll_speed
            # Clamp scrolling to valid range
            self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

        # Handle clicks on slots
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Check if click is within visible area
            if self.visible_area.collidepoint(mouse_x, mouse_y):
                # Calculate which slot was clicked
                adjusted_y = mouse_y - self.visible_area.top + self.scroll_y
                slot_index = int(adjusted_y / (self.slot_height + self.slot_spacing))

                if 0 <= slot_index < len(self.save_slots):
                    # Normal slot selection
                    print(f"Selected slot: {self.save_slots[slot_index]}")
                    self.selected_slot = slot_index

    def draw(self):
        """Draw all UI elements."""
        if not self.visible:
            return

        # Draw background for the scrollable area
        pygame.draw.rect(self.screen, (20, 20, 20), self.visible_area)
        pygame.draw.rect(self.screen, self.slot_border_color, self.visible_area, self.border_thickness)

        # Create a clipping rect for the visible area
        original_clip = self.screen.get_clip()
        self.screen.set_clip(self.visible_area)

        # Draw all slots
        for i, slot_text in enumerate(self.save_slots):
            # Calculate position with scrolling offset
            slot_y = self.visible_area.top + i * (self.slot_height + self.slot_spacing) - self.scroll_y
            slot_rect = pygame.Rect(self.visible_area.left, slot_y, self.slot_width, self.slot_height)

            # Skip slots that are outside the visible area
            if slot_rect.bottom < self.visible_area.top or slot_rect.top > self.visible_area.bottom:
                continue

            # Draw slot background
            bg_color = self.selected_slot_color if i == self.selected_slot else self.slot_background_color
            pygame.draw.rect(self.screen, bg_color, slot_rect)
            pygame.draw.rect(self.screen, self.slot_border_color, slot_rect, self.border_thickness)

            # Draw slot text
            text_surface = self.font.render(slot_text, True, self.text_color)
            text_rect = text_surface.get_rect(midleft=(slot_rect.left + 20, slot_rect.centery))
            self.screen.blit(text_surface, text_rect)

            # X buttons removed as requested

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

        # Draw back button
        self.back_button.draw()

    def show(self):
        """Show the custom mode screen."""
        self.visible = True
        self.scroll_y = 0  # Reset scroll position

    def hide(self):
        """Hide the custom mode screen."""
        self.visible = False
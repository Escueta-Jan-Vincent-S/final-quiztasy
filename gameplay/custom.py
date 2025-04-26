import pygame
import os
from ui.button import Button
from ui.back_button import BackButton
from auth.input_box import InputBox
from settings import FONT_PATH, FONT_SIZE
from managers.custom_manager import CustomManager
import datetime
import sys


class CustomMode:
    def __init__(self, screen, audio_manager, script_dir, scale=0.5, game_instance=None):
        self.game_instance = game_instance
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
        create_btn_path = os.path.join(script_dir, "assets", "images", "buttons", "game modes", "custom", "createquestion_btn_img.png")
        create_btn_hover_path = os.path.join(script_dir, "assets", "images", "buttons", "game modes", "custom", "createquestion_btn_hover.png")

        self.create_button = Button(960, 875, create_btn_path, create_btn_hover_path, None, self.create_question, scale=0.5, audio_manager=self.audio_manager)

        # Back Button
        self.back_button = BackButton(self.screen, script_dir, self.go_back, audio_manager=self.audio_manager, position=(100, 100), scale=0.25)
        self.update_max_scroll()

        # Question creation state
        self.creating_question = False
        self.current_questions = []  # Store questions during creation

        # Status message for validation (similar to login screen)
        self.status_message = ""
        self.status_color = pygame.Color('white')
        self.status_timer = 0  # Timer to clear the message after some time

        # Load input border
        input_border_path = os.path.join(script_dir, "assets", "images", "buttons", "game modes", "custom", "input_border.png")
        self.input_border = pygame.image.load(input_border_path).convert_alpha()
        self.input_border = pygame.transform.scale(self.input_border,(int(self.input_border.get_width() * 0.7), int(self.input_border.get_height() * 0.7)))
        self.input_border_rect = self.input_border.get_rect(center=(960, 500))

        # Input boxes for question and answer with updated parameters
        self.question_input = InputBox(310, 290, 1300, 260,
                                       placeholder="Enter your question here...", align_top_left=True, multiline=True)
        self.answer_input = InputBox(310, 700, 1300, 120,
                                     placeholder="Enter the answer here...", align_top_left=True)

        # Next and Done buttons
        next_btn_path = os.path.join(script_dir, "assets", "images", "buttons", "game modes", "custom", "next_btn_img.png")
        next_btn_hover_path = os.path.join(script_dir, "assets", "images", "buttons", "game modes", "custom", "next_btn_hover.png")
        done_btn_path = os.path.join(script_dir, "assets", "images", "buttons", "game modes", "custom", "done_btn_img.png")
        done_btn_hover_path = os.path.join(script_dir, "assets", "images", "buttons", "game modes", "custom", "done_btn_hover.png")

        self.next_button = Button(700, 950, next_btn_path, next_btn_hover_path, None, self.next_question, scale=0.5,audio_manager=self.audio_manager)
        self.done_button = Button(1200, 950, done_btn_path, done_btn_hover_path, None, self.done_creating, scale=0.5, audio_manager=self.audio_manager)

        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.custom_manager = CustomManager()

    def update_max_scroll(self):
        """Update the maximum scrolling value based on content height."""
        total_height = len(self.save_slots) * (self.slot_height + self.slot_spacing)
        visible_height = self.visible_area.height
        self.max_scroll = max(0, total_height - visible_height)

    def create_question(self):
        """Handle create button click."""
        print("Create Question Clicked")
        # Show the question creation interface
        self.creating_question = True
        self.current_questions = []
        self.question_input.text = ""
        self.answer_input.text = ""
        self.status_message = ""

    def next_question(self):
        """Save current question and clear inputs for next question."""
        question = self.question_input.text.strip()
        answer = self.answer_input.text.strip()

        if question and answer:
            self.current_questions.append({"question": question, "answer": answer})
            self.question_input.text = ""
            self.answer_input.text = ""
            self.status_message = f"Question added successfully. Total: {len(self.current_questions)}"
            self.status_color = pygame.Color('green')
            self.status_timer = pygame.time.get_ticks()  # Start timer
        else:
            self.status_message = "Please enter both question and answer before proceeding"
            self.status_color = pygame.Color('red')
            self.status_timer = pygame.time.get_ticks()  # Start timer

    def done_creating(self):
        """Finish creating questions and save to database."""
        # First check if there are any questions or if current fields are filled
        question = self.question_input.text.strip()
        answer = self.answer_input.text.strip()

        # Add the current question if fields are filled
        if question and answer:
            self.current_questions.append({"question": question, "answer": answer})

        if not self.current_questions:
            self.status_message = "Please add at least one question before finishing"
            self.status_color = pygame.Color('red')
            self.status_timer = pygame.time.get_ticks()  # Start timer
            return

        # Generate a name based on current date/time
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        question_set_name = f"Questions - {current_date}"

        # Save to database via custom manager
        self.custom_manager.save_question_set(question_set_name, self.current_questions)

        # Update slot list
        self.save_slots = self.custom_manager.get_question_sets()
        self.update_max_scroll()

        self.status_message = f"Saved {len(self.current_questions)} questions as '{question_set_name}'"
        self.status_color = pygame.Color('green')

        # Set timer to exit question creation mode after showing success message
        pygame.time.set_timer(pygame.USEREVENT + 2, 1500)  # Exit after 1.5 seconds

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
        if self.creating_question:
            # If in question creation mode, go back to slot selection
            self.creating_question = False
            return

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

        # Check if timer to close question creation mode has elapsed
        if event.type == pygame.USEREVENT + 2:
            pygame.time.set_timer(pygame.USEREVENT + 2, 0)  # Stop the timer
            self.creating_question = False
            return

        self.back_button.update(event)

        if self.creating_question:
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

        # Draw back button
        self.back_button.draw()

        if self.creating_question:
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
            count_text = f"Questions added: {len(self.current_questions)}"
            count_surface = self.small_font.render(count_text, True, self.text_color)
            self.screen.blit(count_surface, (self.question_input.rect.x, 260    ))

            # Draw status message if any
            if self.status_message:
                status_surf = self.font.render(self.status_message, True, self.status_color)
                status_x = 960 - status_surf.get_width() // 2  # Center horizontally
                status_y = 850  # Position above the buttons
                self.screen.blit(status_surf, (status_x, status_y))
        else:
            # Draw slots view
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

    def show(self):
        """Show the custom mode screen."""
        self.visible = True
        self.scroll_y = 0  # Reset scroll position
        # Load question sets from database
        self.save_slots = self.custom_manager.get_question_sets()
        self.update_max_scroll()

    def hide(self):
        """Hide the custom mode screen."""
        self.visible = False
        self.creating_question = False
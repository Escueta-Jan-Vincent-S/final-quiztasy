import pygame
import time
import os
import random
from characters.player import Player
from gameplay.questions import QuestionGenerator
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, FONT_PATH
from .pause import Pause
from .coin_toss import CoinToss


class PVPBattle:
    def __init__(self, screen, script_dir, p1_hero="boy", p2_hero="girl", audio_manager=None, game_instance=None):
        self.screen = screen
        self.script_dir = script_dir
        self.running = True
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_PATH, 50)
        self.small_font = pygame.font.Font(FONT_PATH, 30)
        self.turn_font = pygame.font.Font(FONT_PATH, 40)
        self.audio_manager = audio_manager
        self.game_instance = game_instance

        self.timer_seconds = 15  # Default time for questions
        self.difficulty = 1

        # Initialize players with their chosen heroes
        self.player1 = Player(script_dir, p1_hero)
        self.player2 = Player(script_dir, p2_hero)

        # Disable the built-in health bars in the Player class
        self.player1.show_health_bar = False
        self.player2.show_health_bar = False

        # Set player positions properly (left and right sides)
        self.player1.rect.x = 300  # Left side position
        self.player1.rect.bottom = 700

        self.player2.rect.x = SCREEN_WIDTH - 475  # Right side position
        self.player2.rect.bottom = 700
        self.player2.image = pygame.transform.flip(self.player2.image, True, False)

        # Determine which player goes first with a coin toss
        self.coin_toss = CoinToss(screen, script_dir, audio_manager, battle_instance=self)
        self.first_player = None  # Will be set after coin toss

        # Battle state
        self.current_player = None  # Will be set after coin toss
        self.current_question = None
        self.selected_answer = None
        self.answer_buttons = []
        self.timer_start = 0
        self.battle_message = ""
        self.message_timer = 0

        # Initialize pause menu with specific callbacks
        self.pause_menu = Pause(
            screen,
            script_dir,
            audio_manager,
            menu_callback=self.return_to_menu_from_pause
        )

        # Load battle music
        self.battle_music = self.load_battle_music()

        print(f"PVP Battle initialized with Player 1: {p1_hero}, Player 2: {p2_hero}")

    def return_to_menu_from_pause(self):
        """Handle returning to main menu when selected from pause menu"""
        print("Returning to main menu from pause menu")
        self.running = False  # End current battle
        if self.game_instance:
            self.game_instance.return_to_main_menu()
        else:
            print("No game instance")

    def load_battle_music(self):
        """Load a random PVP battle music track."""
        # Choose one of the three available PVP battle OSTs randomly
        random_track = random.randint(1, 3)
        return os.path.join(self.script_dir, "assets", "audio", "ost", "battle", f"pvp_battle_ost_{random_track}.mp3")

    def stop_battle_music(self):
        """Stop the battle music."""
        pygame.mixer.music.stop()

    def start_battle(self):
        """Start the PVP battle with a coin toss to determine first player."""
        # Run the coin toss to determine who goes first
        self.first_player = self.coin_toss.run()
        if self.first_player is None:  # User closed the game during coin toss
            self.running = False
            return

        self.current_player = self.first_player

        # Play battle music
        if self.battle_music:
            pygame.mixer.music.load(self.battle_music)
            pygame.mixer.music.play(-1)  # Loop the battle music

        # Generate the first question
        self.generate_new_question()

    def generate_new_question(self):
        """Generates a new question for the battle"""
        self.current_question = QuestionGenerator.get_random_question(self.difficulty)  # Use self.difficulty
        self.timer_start = time.time()
        self.time_left = self.timer_seconds  # Use self.timer_seconds
        self.selected_answer = None
        self.create_answer_buttons()

    def create_answer_buttons(self):
        """Creates the answer buttons based on the current question"""
        self.answer_buttons = []
        # Create a button for each choice
        button_width = 200
        button_height = 60
        button_margin = 20
        total_width = (button_width + button_margin) * len(self.current_question.choices)
        start_x = (SCREEN_WIDTH - total_width) // 2

        for i, choice in enumerate(self.current_question.choices):
            button_rect = pygame.Rect(
                start_x + i * (button_width + button_margin),
                SCREEN_HEIGHT - 150,
                button_width,
                button_height
            )
            self.answer_buttons.append({
                'rect': button_rect,
                'value': choice,
                'text': str(choice),
                'hovered': False
            })

    def handle_events(self):
        """Handle user input during battle"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Only process other events if not paused
            if not self.pause_menu.is_paused():
                if event.type == pygame.MOUSEMOTION:
                    # Check if mouse is hovering over any answer button
                    mouse_pos = pygame.mouse.get_pos()
                    for button in self.answer_buttons:
                        button['hovered'] = button['rect'].collidepoint(mouse_pos)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if an answer button was clicked
                    mouse_pos = pygame.mouse.get_pos()
                    for button in self.answer_buttons:
                        if button['rect'].collidepoint(mouse_pos):
                            self.selected_answer = button['value']
                            self.check_answer()

            # Always process pause menu events
            self.pause_menu.update(event)

    def check_answer(self):
        """Checks if the selected answer is correct"""
        current = self.player1 if self.current_player == 1 else self.player2
        opponent = self.player2 if self.current_player == 1 else self.player1

        if self.selected_answer == self.current_question.answer:
            # Correct answer - opponent takes damage
            opponent.take_damage(1)
            self.battle_message = f"Correct! Player {3 - self.current_player} takes damage!"

            if opponent.hp <= 0:
                self.battle_message = f"Victory! Player {self.current_player} wins!"
                # Wait a bit before ending the battle
                pygame.time.delay(2000)
                self.running = False  # End the battle
        else:
            # Wrong answer - current player takes damage
            current.take_damage(1)
            self.battle_message = f"Wrong! Player {self.current_player} takes damage!"

            if current.hp <= 0:
                self.battle_message = f"Victory! Player {3 - self.current_player} wins!"
                # Wait a bit before ending the battle
                pygame.time.delay(2000)
                self.running = False  # End the battle

        # Set message timer
        self.message_timer = time.time()

        # Switch to the other player's turn
        self.current_player = 3 - self.current_player  # Toggle between 1 and 2

        # Generate a new question for the next player
        self.generate_new_question()

    def update_timer(self):
        """Updates the time left to answer the question"""
        # If paused, don't update anything
        if self.pause_menu.is_paused():
            return

        # Adjust timer for any time spent paused
        paused_time = self.pause_menu.get_total_paused_time()
        if paused_time > 0:
            self.timer_start += paused_time  # Move the start time forward by paused duration

        # Calculate remaining time
        elapsed = time.time() - self.timer_start
        self.time_left = max(0, self.timer_seconds - elapsed)

        # If time runs out, treat as wrong answer
        if self.time_left <= 0 and self.running:
            current = self.player1 if self.current_player == 1 else self.player2

            self.battle_message = f"Time's up! Player {self.current_player} takes damage!"
            current.take_damage(1)

            if current.hp <= 0:
                self.battle_message = f"Victory! Player {3 - self.current_player} wins!"
                # Wait a bit before ending the battle
                pygame.time.delay(2000)
                self.running = False  # End the battle
            else:
                # Switch to the other player's turn
                self.current_player = 3 - self.current_player
                # Generate a new question for the next player
                self.generate_new_question()

            # Set message timer
            self.message_timer = time.time()

    def draw_background_for_coin_toss(self):
        """Draws only the background for the coin toss, without UI elements that need game state."""
        # Draw background
        self.screen.fill((50, 50, 100))

        # Draw players with their correct positions
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)

        # Draw player health bars (which don't change during coin toss)
        self.draw_health_bar(self.player1, SCREEN_WIDTH // 4, 30, "Player 1")
        self.draw_health_bar(self.player2, 3 * SCREEN_WIDTH // 4, 30, "Player 2")

    def draw(self):
        """Draws the battle screen"""
        # Draw background
        self.screen.fill((50, 50, 100))

        # Draw players in their proper positions
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)

        # Draw timer
        timer_text = self.font.render(f"Time: {int(self.time_left)}", True, (255, 255, 255))
        timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        pygame.draw.rect(self.screen, (0, 0, 0), (timer_rect.x - 10, timer_rect.y - 10, timer_rect.width + 20, timer_rect.height + 20))
        self.screen.blit(timer_text, timer_rect)

        # Draw current player turn indicator
        turn_text = self.turn_font.render(f"Player {self.current_player}'s Turn", True, (0, 255, 0) if self.current_player == 1 else (0, 200, 255))
        turn_rect = turn_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        pygame.draw.rect(self.screen, (0, 0, 0), (turn_rect.x - 10, turn_rect.y - 10, turn_rect.width + 20, turn_rect.height + 20))
        self.screen.blit(turn_text, turn_rect)

        # Draw question box
        question_box = pygame.Rect(50, SCREEN_HEIGHT - 300, SCREEN_WIDTH - 100, 200)
        pygame.draw.rect(self.screen, (0, 0, 0, 200), question_box)
        pygame.draw.rect(self.screen, (255, 255, 255), question_box, 3)

        # Draw question text
        question_text = self.font.render(self.current_question.question_text, True, (255, 255, 255))
        question_rect = question_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 250))
        self.screen.blit(question_text, question_rect)

        # Draw answer buttons if not paused
        if not self.pause_menu.is_paused():
            for button in self.answer_buttons:
                color = (100, 100, 255) if button['hovered'] else (50, 50, 200)
                pygame.draw.rect(self.screen, color, button['rect'])
                pygame.draw.rect(self.screen, (255, 255, 255), button['rect'], 2)
                text = self.small_font.render(button['text'], True, (255, 255, 255))
                text_rect = text.get_rect(center=button['rect'].center)
                self.screen.blit(text, text_rect)

        # Draw battle message
        if self.battle_message and time.time() - self.message_timer < 2:
            message_text = self.font.render(self.battle_message, True, (255, 255, 0))
            message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            pygame.draw.rect(self.screen, (0, 0, 0),(message_rect.x - 10, message_rect.y - 10, message_rect.width + 20, message_rect.height + 20))
            self.screen.blit(message_text, message_rect)

        # Draw player health bars
        self.draw_health_bar(self.player1, SCREEN_WIDTH // 4, 30, "Player 1")
        self.draw_health_bar(self.player2, 3 * SCREEN_WIDTH // 4, 30, "Player 2")

        # Draw pause menu
        self.pause_menu.draw()

    def draw_health_bar(self, player, x, y, label):
        """Draw a health bar for the given player at the specified position."""
        # Draw label
        label_text = self.small_font.render(label, True, (255, 255, 255))
        label_rect = label_text.get_rect(center=(x, y))
        self.screen.blit(label_text, label_rect)

        # Draw health bar background
        bar_width = 200
        bar_height = 20
        bar_bg_rect = pygame.Rect(x - bar_width // 2, y + 20, bar_width, bar_height)
        pygame.draw.rect(self.screen, (100, 0, 0), bar_bg_rect)

        # Draw current health
        health_percentage = max(0, player.hp / player.max_hp)
        health_width = int(bar_width * health_percentage)
        health_rect = pygame.Rect(x - bar_width // 2, y + 20, health_width, bar_height)
        pygame.draw.rect(self.screen, (0, 200, 0), health_rect)

        # Draw border
        pygame.draw.rect(self.screen, (255, 255, 255), bar_bg_rect, 2)

        # Draw health text
        health_text = self.small_font.render(f"{player.hp}/{player.max_hp}", True, (255, 255, 255))
        health_text_rect = health_text.get_rect(center=(x, y + 20 + bar_height // 2))
        self.screen.blit(health_text, health_text_rect)

    def run(self):
        """Main battle loop"""
        # Start with the coin toss
        self.start_battle()

        while self.running:
            # Handle events
            self.handle_events()

            # Update timer
            self.update_timer()

            # Draw battle
            self.draw()

            # Update display
            pygame.display.flip()

            # Cap the frame rate
            self.clock.tick(FPS)

        # Stop battle music when the battle ends
        self.stop_battle_music()

        # Explicitly restart menu music if game_instance is available
        if self.game_instance and hasattr(self.game_instance, 'audio_manager'):
            self.game_instance.audio_manager.music_path = os.path.join(self.script_dir, "assets", "audio", "ost",
                                                                       "menuOst.mp3")
            if hasattr(self.game_instance.audio_manager,
                       'audio_enabled') and self.game_instance.audio_manager.audio_enabled:
                self.game_instance.audio_manager.play_music()
                print("Menu music restarted in battle class")

        # Return result (1 for player 1 victory, 2 for player 2 victory)
        if self.player2.hp <= 0:
            return 1
        elif self.player1.hp <= 0:
            return 2
        else:
            return None  # Battle was interrupted
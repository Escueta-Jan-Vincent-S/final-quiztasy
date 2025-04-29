import pygame
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from ui.back_button import BackButton
from .map_character_movement import MapCharacterMovement
from ui.button import Button
from managers.level_manager import Levels

class Map:
    def __init__(self, screen, script_dir, go_back_callback, audio_manager, hero_type=None, game_instance=None):
        """Initialize the LSPU map with a Back button and navigation features."""
        self.script_dir = script_dir
        self.screen = screen
        self.running = True
        self.go_back_callback = go_back_callback  # Store the callback function
        self.audio_manager = audio_manager

        # Set the hero type (boy or girl)
        self.hero_type = hero_type if hero_type else "boy"  # Default to boy if not specified

        # Store the game instance
        self.game_instance = game_instance

        # Play hero-specific OST if audio is enabled
        if self.audio_manager.audio_enabled:
            self.audio_manager.play_music()

        # Load and scale the map
        self.map_original = pygame.image.load(os.path.join(script_dir, "assets", "images", "map", "lspu_map.png"))
        SCALE_FACTOR = 3
        self.map_width = int(self.map_original.get_width() * SCALE_FACTOR)
        self.map_height = int(self.map_original.get_height() * SCALE_FACTOR)
        self.map = pygame.transform.scale(self.map_original, (self.map_width, self.map_height))

        # Initial map position - center the map
        self.map_x = (SCREEN_WIDTH - self.map_width) // 2
        self.map_y = (SCREEN_HEIGHT - self.map_height) // 2

        # Initialize the Back button
        self.back_button = BackButton(screen, script_dir, self.go_back, position=(100, 100), scale=0.25)

        # Initialize character movement handler
        self.character_movement = MapCharacterMovement(
            self.hero_type,
            self.script_dir,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2
        )

        # Initialize levels
        self.levels_manager = Levels(script_dir)
        # Pass screen, hero_type, audio_manager AND game_instance to the levels manager
        self.levels_manager.set_context(
            self.screen,
            self.hero_type,
            self.audio_manager,
            game_instance=self.game_instance  # Assuming Map is created with game_instance reference
        )

        # Initialize enter button (but don't create it yet - will be created dynamically)
        self.enter_button = None

        # Initialize clock for the run method
        self.clock = pygame.time.Clock()

        # Set the character to spawn at level 0
        self.spawn_at_level(0)

    def spawn_at_level(self, level_id):
        """Spawn the character at the specified level."""
        # Get the level by ID
        level = self.levels_manager.get_level_by_id(level_id)
        if level:
            # Calculate map position to center the character on the level
            character_screen_x = SCREEN_WIDTH // 2
            character_screen_y = SCREEN_HEIGHT // 2 + 50
            # The map needs to be positioned so that the level is under the character
            self.map_x = character_screen_x - level["map_x"] - level["width"] // 2
            self.map_y = character_screen_y - level["map_y"] - level["height"] // 2

            # Ensure map stays within bounds
            map_bounds = {
                'min_x': SCREEN_WIDTH - self.map_width,
                'max_x': 0,
                'min_y': SCREEN_HEIGHT - self.map_height,
                'max_y': 0,
            }
            self.map_x = max(min(self.map_x, map_bounds['max_x']), map_bounds['min_x'])
            self.map_y = max(min(self.map_y, map_bounds['max_y']), map_bounds['min_y'])

    def create_enter_button(self, x, y):
        # Path to button images
        idle_img = os.path.join(self.script_dir, "assets", "images", "buttons", "enter level", "enter_btn_img.png")
        hover_img = os.path.join(self.script_dir, "assets", "images", "buttons", "enter level", "enter_btn_hover.png")
        # Create button - now using the levels_manager's enter_level method
        self.enter_button = Button(x=x, y=y, idle_img=idle_img, hover_img=hover_img, action=self.levels_manager.enter_level, scale=0.5, audio_manager=self.audio_manager)

    def go_back(self):
        if self.audio_manager:
            self.audio_manager.play_sfx()  # Play sound effect when clicking back
        if self.go_back_callback:
            self.go_back_callback()  # Call the callback to return to the main menu
        self.running = False  # Stop the map loop

    def move_character(self):
        """Handle character movement based on keyboard input."""
        # Get map boundaries for character movement
        map_bounds = {
            'min_x': SCREEN_WIDTH - self.map_width,
            'max_x': 0,
            'min_y': SCREEN_HEIGHT - self.map_height,
            'max_y': 0,
            'width': self.map_width,
            'height': self.map_height
        }
        # Call the character movement handler
        map_adjustment, character_pos = self.character_movement.handle_movement(
            map_bounds,
            (self.map_x, self.map_y),
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        # Update map position
        self.map_x = map_adjustment[0]
        self.map_y = map_adjustment[1]
        # Check for level proximity after movement
        self.check_level_proximity(character_pos)

    def check_level_proximity(self, character_pos):
        """Check if character is near a level to display the enter button."""
        char_x, char_y = character_pos
        # Convert character screen position to map position
        char_map_x = char_x - self.map_x
        char_map_y = char_y - self.map_y

        nearby_level_id = self.levels_manager.check_proximity(char_map_x, char_map_y)
        if nearby_level_id is not None and nearby_level_id != 0:
            # Set active level in the levels manager
            self.levels_manager.set_active_level(nearby_level_id)

            # Create or update enter button position
            button_x = char_x
            button_y = char_y + 125

            if self.enter_button is None:
                self.create_enter_button(button_x, button_y)
            else:
                # Update button position
                self.enter_button.rect.centerx = button_x
                self.enter_button.rect.centery = button_y

            self.enter_button.visible = True
        else:
            # Hide button if not near any level
            if self.enter_button:
                self.enter_button.visible = False
            # Clear active level in the levels manager
            self.levels_manager.set_active_level(None)

    def draw(self):
        """Draw the map, levels, and player icon on the screen."""
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.map, (self.map_x, self.map_y))
        # Draw levels on the map using the levels manager
        self.levels_manager.draw_levels(self.screen, self.map_x, self.map_y)
        # Draw character
        self.character_movement.draw(self.screen)
        # Draw enter button if it exists and is visible
        if self.enter_button and self.enter_button.visible:
            self.enter_button.draw(self.screen)
        # Draw back button
        self.back_button.draw()

    def handle_events(self):
        """Handle map interactions and level selection."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Handle back button
            self.back_button.update(event)

            # Handle enter button if it exists and is visible
            if self.enter_button and self.enter_button.visible:
                self.enter_button.update(event)

    def update_character_animation(self):
        """Update character animation frames"""
        self.character_movement.update_animation()

    def run(self):
        """Main map loop."""
        while self.running:
            # Handle events
            self.handle_events()
            # Handle character movement - this should be called every frame
            self.move_character()
            # Update animation
            self.update_character_animation()
            # Draw everything
            self.draw()
            # Update display
            pygame.display.flip()
            # Cap the frame rate
            self.clock.tick(FPS)
import pygame
import os
import random
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from back_button import BackButton


class Map:
    def __init__(self, screen, script_dir, go_back_callback, audio_manager, hero_type=None):
        """Initialize the LSPU map with a Back button and navigation features."""
        self.script_dir = script_dir
        self.screen = screen
        self.running = True
        self.dragging = False
        self.last_mouse_x, self.last_mouse_y = 0, 0
        self.go_back_callback = go_back_callback  # Store the callback function
        self.audio_manager = audio_manager

        # Set the hero type (boy or girl)
        self.hero_type = hero_type if hero_type else "boy"  # Default to boy if not specified

        # Play hero-specific OST if audio is enabled
        if self.audio_manager.audio_enabled:
            self.audio_manager.play_music()

        # Load and scale the map
        self.map_original = pygame.image.load(os.path.join(script_dir, "images", "map", "lspu_map.png"))
        SCALE_FACTOR = 1.5
        self.map_width = int(self.map_original.get_width() * SCALE_FACTOR)
        self.map_height = int(self.map_original.get_height() * SCALE_FACTOR)
        self.map = pygame.transform.scale(self.map_original, (self.map_width, self.map_height))

        # Initial map position
        self.map_x, self.map_y = 0, 0

        # Initialize the Back button
        self.back_button = BackButton(screen, script_dir, self.go_back, position=(100, 100), scale=0.25)

        # Load player icon based on hero type
        icon_path = os.path.join(script_dir, "images", "map", "icons", f"{self.hero_type}_head_img.png")
        try:
            self.player_icon = pygame.image.load(icon_path)
            self.player_icon = pygame.transform.scale(self.player_icon, (100, 120))
        except pygame.error:
            print(f"Warning: Could not load {icon_path}. Using placeholder.")
            # Create a placeholder icon if file not found
            self.player_icon = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(self.player_icon, (255, 255, 0), (25, 25), 25)

        # Define levels (black dots) coordinates relative to map
        self.levels = [
            {"id": 0, "pos": (245, 470), "completed": False},
            {"id": 1, "pos": (420, 470), "completed": False},
            {"id": 2, "pos": (550, 150), "completed": False},
            {"id": 3, "pos": (800, 460), "completed": False},
            {"id": 4, "pos": (800, 230), "completed": False},
            {"id": 5, "pos": (1150, 325), "completed": False},
            {"id": 6, "pos": (1360, 235), "completed": False},
            {"id": 7, "pos": (1505, 590), "completed": False},
            {"id": 8, "pos": (1420, 1005), "completed": False},
            {"id": 9, "pos": (1480, 1150), "completed": False},
            {"id": 10, "pos": (1910, 1335), "completed": False},
            {"id": 11, "pos": (1750, 1060), "completed": False},
            {"id": 12, "pos": (2390, 1075), "completed": False},
            {"id": 13, "pos": (2390, 780), "completed": False},
            {"id": 14, "pos": (2196, 732), "completed": False},
            {"id": 15, "pos": (1770, 460), "completed": False},
            {"id": 16, "pos": (1880, 115), "completed": False},
            {"id": 17, "pos": (1990, 285), "completed": False},
            {"id": 18, "pos": (2287, 493), "completed": False},
            {"id": 19, "pos": (2425, 300), "completed": False},
            {"id": 20, "pos": (2425, 75), "completed": False},
        ]

        # Define ambush points (red dots A) with 25% chance of triggering
        self.ambush_points = [
            {"pos": (1030, 450), "triggered": False, "chance": 25},
            {"pos": (1505, 300), "triggered": False, "chance": 25},
            {"pos": (1445, 1310), "triggered": False, "chance": 25},
            {"pos": (1870, 732), "triggered": False, "chance": 25},
            {"pos": (2080, 493), "triggered": False, "chance": 25},
            {"pos": (2545, 300), "triggered": False, "chance": 25},
        ]

        # Current player position (starting at level 1)
        self.current_level = 0
        self.player_pos = self.levels[0]["pos"]
        self.moving = False
        self.movement_path = []
        self.movement_speed = 5

        # Font for level numbers
        self.font = pygame.font.SysFont('Arial', 15)

    def go_back(self):
        """Handle back button action."""
        if self.audio_manager:
            self.audio_manager.play_sfx()  # Play sound effect when clicking back
        if self.go_back_callback:
            self.go_back_callback()  # Call the callback to return to the main menu
        self.running = False  # Stop the map loop

    def move_to_level(self, level_id):
        """Set up movement path to the selected level."""
        if level_id in [level["id"] for level in self.levels]:  # Ensure the level exists
            if (self.current_level == 0 and level_id == 1) or \
                    (isinstance(self.current_level, int) and abs(self.current_level - level_id) == 1):
                target_pos = next(level["pos"] for level in self.levels if level["id"] == level_id)
                self.movement_path = self.generate_path(self.player_pos, target_pos)
                self.moving = True
                self.current_level = level_id
                return True
        return False

    def generate_path(self, start, end):
        """Generate a simple linear path between two points."""
        # For a more complex path, you'd implement pathfinding along the green lines
        # This is a simplified direct path
        path = []
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        steps = max(abs(dx), abs(dy)) // self.movement_speed

        if steps > 0:
            for i in range(steps + 1):
                x = start[0] + (dx * i) // steps
                y = start[1] + (dy * i) // steps
                path.append((x, y))

        return path

    def check_ambush(self):
        """Check if player has triggered an ambush."""
        for ambush in self.ambush_points:
            # Calculate distance to ambush point
            ambush_x, ambush_y = ambush["pos"]
            player_x, player_y = self.player_pos
            distance = ((ambush_x - player_x) ** 2 + (ambush_y - player_y) ** 2) ** 0.5

            # If player is near an ambush point and it hasn't been triggered
            if distance < 30 and not ambush["triggered"]:
                # 25% chance of ambush
                if random.randint(1, 100) <= ambush["chance"]:
                    ambush["triggered"] = True
                    print("AMBUSH TRIGGERED!")
                    return True
        return False

    def update_movement(self):
        """Update player position along the movement path."""
        if self.moving and self.movement_path:
            # Move to next point in path
            self.player_pos = self.movement_path.pop(0)

            # Check if we've reached the end of the path
            if not self.movement_path:
                self.moving = False
                self.levels[self.current_level - 1]["completed"] = True

                # Check for ambush after completing movement
                if self.check_ambush():
                    print("AMBUSH! Battle initiated!")
                    # Here you would trigger battle mode

    def draw(self):
        """Draw the map, levels, and player icon on the screen."""
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.map, (self.map_x, self.map_y))

        # Draw levels (black dots)
        for level in self.levels:
            adjusted_pos = (self.map_x + level["pos"][0], self.map_y + level["pos"][1])

            # Draw level dot
            color = (0, 255, 0) if level["completed"] else (0, 0, 0)
            pygame.draw.circle(self.screen, color, adjusted_pos, 10)

            # Draw level number
            level_text = self.font.render(str(level["id"]), True, (255, 255, 255))
            self.screen.blit(level_text, (adjusted_pos[0] - 5, adjusted_pos[1] - 10))

        # Draw ambush points (marked as 'A')
        for ambush in self.ambush_points:
            adjusted_pos = (self.map_x + ambush["pos"][0], self.map_y + ambush["pos"][1])

            # Draw ambush indicator (if not already triggered)
            if not ambush["triggered"]:
                pygame.draw.circle(self.screen, (255, 0, 0), adjusted_pos, 10)
                ambush_text = self.font.render("A", True, (255, 255, 255))
                self.screen.blit(ambush_text, (adjusted_pos[0] - 5, adjusted_pos[1] - 10))

        # Draw player icon
        adjusted_player_pos = (self.map_x + self.player_pos[0] - 25, self.map_y + self.player_pos[1] - 25)
        self.screen.blit(self.player_icon, adjusted_player_pos)

        # Draw back button
        self.back_button.draw()

    def handle_events(self):
        """Handle map interactions and level selection."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            self.back_button.update(event)

            # Handle dragging and level selection
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos

                # Check if clicked on a level
                for level in self.levels:
                    adjusted_pos = (self.map_x + level["pos"][0], self.map_y + level["pos"][1])
                    distance = ((mouse_x - adjusted_pos[0]) ** 2 + (mouse_y - adjusted_pos[1]) ** 2) ** 0.5

                    if distance < 15 and not self.moving:
                        if self.move_to_level(level["id"]):
                            print(f"Moving to level {level['id']}")
                            break

                # If no level was clicked, start dragging
                if not self.moving:
                    self.dragging = True
                    self.last_mouse_x, self.last_mouse_y = event.pos

            elif event.type == pygame.MOUSEMOTION and self.dragging:
                dx = event.pos[0] - self.last_mouse_x
                dy = event.pos[1] - self.last_mouse_y
                self.map_x += dx
                self.map_y += dy
                self.last_mouse_x, self.last_mouse_y = event.pos

                # Constrain map position
                self.map_x = max(min(0, self.map_x), SCREEN_WIDTH - self.map_width)
                self.map_y = max(min(0, self.map_y), SCREEN_HEIGHT - self.map_height)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False
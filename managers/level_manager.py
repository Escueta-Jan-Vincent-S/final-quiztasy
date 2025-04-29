import pygame
import os
from gameplay.battle import Battle
from gameplay.levels import Level  # Combined Level class

class Levels:
    def __init__(self, script_dir):
        """Initialize the levels with their positions and attributes."""
        self.script_dir = script_dir
        self.levels = []
        self.level_images = {}
        self.active_level = None
        self.screen = None
        self.hero_type = None
        self.audio_manager = None
        self.game_instance = None
        self.load_levels()

    def load_levels(self):
        """Load level sprites and define their positions on the map."""
        LEVEL_SCALE = 0.15
        level_names = ["spawn_point"] + [f"stage_{i}" for i in range(1, 21)]  # Includes spawn and 20 levels

        # Load and scale images once
        for name in level_names:
            image_path = os.path.join(self.script_dir, "assets", "images", "levels", f"{name}.png")
            original_img = pygame.image.load(image_path)
            scaled_img = pygame.transform.scale(
                original_img,
                (
                    int(original_img.get_width() * LEVEL_SCALE),
                    int(original_img.get_height() * LEVEL_SCALE)
                )
            )
            self.level_images[name] = scaled_img

        # Define level positions and interaction radii
        level_data = [
            (0, "spawn_point", 1930, 1830, 0),
            (1, "stage_1", 3000, 1830, 75),
            (2, "stage_2", 4190, 1450, 75),
            (3, "stage_3", 3375, 550, 75),
            (4, "stage_4", 4715, 2575, 75),
            (5, "stage_5", 5400, 1775, 75),
            (6, "stage_6", 6350, 1225, 75),
            (7, "stage_7", 6350, 2700, 75),
            (8, "stage_8", 6300, 4500, 75),
            (9, "stage_9", 6300, 6400, 75),
            (10, "stage_10", 7880, 6150, 75),
            (11, "stage_11", 9700, 4700, 75),
            (12, "stage_12", 9600, 3050, 75),
            (13, "stage_13", 7550, 4700, 75),
            (14, "stage_14", 6830, 3550, 75),
            (15, "stage_15", 7160, 1735, 75),
            (16, "stage_16", 7975, 1835, 75),
            (17, "stage_17", 8465, 1000, 75),
            (18, "stage_18", 9050, 1835, 75),
            (19, "stage_19", 9825, 1600, 75),
            (20, "stage_20", 9700, 600, 75),
        ]

        self.levels = [
            {
                "id": lvl_id,
                "img": self.level_images[name],
                "map_x": x,
                "map_y": y,
                "width": self.level_images[name].get_width(),
                "height": self.level_images[name].get_height(),
                "interaction_radius": radius,
                "unlocked": lvl_id == 1  # Only level 1 is unlocked by default
            }
            for lvl_id, name, x, y, radius in level_data
        ]

    def set_context(self, screen, hero_type, audio_manager=None, game_instance=None):
        """Set the screen, hero type, audio_manager and game_instance needed for the enter_level method."""
        self.screen = screen
        self.hero_type = hero_type
        self.audio_manager = audio_manager
        self.game_instance = game_instance

    def get_level_by_id(self, level_id):
        """Get a level by its ID."""
        return next((l for l in self.levels if l["id"] == level_id), None)

    def get_all_levels(self):
        """Return all levels."""
        return self.levels

    def draw_levels(self, screen, map_x, map_y):
        """Draw all levels on the map at their correct positions."""
        for level in self.levels:
            level_screen_x = map_x + level["map_x"]
            level_screen_y = map_y + level["map_y"]

            if not level["unlocked"]:
                # Dim locked levels
                locked_img = level["img"].copy()
                locked_img.set_alpha(100)
                screen.blit(locked_img, (level_screen_x, level_screen_y))
            else:
                screen.blit(level["img"], (level_screen_x, level_screen_y))

    def check_proximity(self, char_map_x, char_map_y):
        """Check if character is near any level and return the level ID if so."""
        for level in self.levels:
            if not level["unlocked"]:
                continue

            level_center_x = level["map_x"] + level["width"] // 2
            level_center_y = level["map_y"] + level["height"] // 2

            distance = ((char_map_x - level_center_x) ** 2 +
                        (char_map_y - level_center_y) ** 2) ** 0.5

            if distance <= level["interaction_radius"]:
                return level["id"]
        return None

    def set_active_level(self, level_id):
        """Set the active level."""
        level = self.get_level_by_id(level_id)
        if level and level["unlocked"]:
            self.active_level = level_id

    def unlock_level(self, level_id):
        """Unlock a level."""
        if level_id > 20:
            return  # Prevent unlocking beyond max level
        level = self.get_level_by_id(level_id)
        if level:
            level["unlocked"] = True

    def enter_level(self, on_enter=None):
        """Enter the currently active level."""
        if self.active_level is not None and self.screen is not None:
            print(f"Level {self.active_level} is clicked")

            level = Level(self.script_dir, self.active_level)

            battle = Battle(
                self.screen,
                self.script_dir,
                level,
                self.hero_type,
                self.audio_manager,
                game_instance=self.game_instance
            )

            victory = battle.run()

            if victory:
                print(f"Victory! Level {self.active_level} completed.")
                next_level_id = self.active_level + 1
                if next_level_id <= 20:
                    self.unlock_level(next_level_id)
                if on_enter:
                    on_enter(self.active_level, victory=True)
            else:
                print(f"Defeat! Try level {self.active_level} again.")
                if on_enter:
                    on_enter(self.active_level, victory=False)
import pygame
from characters.enemy import MiniBoss

class Level:
    def __init__(self, script_dir, level_id):
        self.script_dir = script_dir
        self.level_id = level_id

        level_settings = {
            1: {"name": "Level 1", "description": "Basta Level 1", "enemy_hp": 5, "enemy_damage": 1,
                "question_difficulty": 1, "timer_seconds": 10},
            2: {"name": "Level 2", "description": "Basta Level 2", "enemy_hp": 6, "enemy_damage": 1.5,
                "question_difficulty": 1, "timer_seconds": 10},
            3: {"name": "Level 3", "description": "Basta Level 3", "enemy_hp": 7, "enemy_damage": 2,
                "question_difficulty": 1, "timer_seconds": 10},
            4: {"name": "Level 4", "description": "Basta Level 4", "enemy_hp": 8, "enemy_damage": 2.5,
                "question_difficulty": 1, "timer_seconds": 10},
            5: {"name": "Level 5", "description": "Basta Level 5", "enemy_hp": 9, "enemy_damage": 3,
                "question_difficulty": 1, "timer_seconds": 10},
        }

        # Get settings for this level or default to level 1 if not found
        settings = level_settings.get(level_id, level_settings[1])

        self.name = settings["name"]
        self.description = settings["description"]
        self.enemy_hp = settings["enemy_hp"]
        self.enemy_damage = settings["enemy_damage"]
        self.question_difficulty = settings["question_difficulty"]
        self.timer_seconds = settings["timer_seconds"]

        # Load background for this level
        self.background = pygame.image.load(f"{script_dir}/assets/images/battle/backgrounds/level1_bg.png")
        self.background = pygame.transform.scale(self.background, (1920, 1080))

    def create_enemy(self):
        """Creates the enemy for this level"""
        return MiniBoss(
            self.script_dir,
            level=self.level_id,
            hp=self.enemy_hp,
            damage=self.enemy_damage
        )

    def get_timer_seconds(self):
        """Returns the number of seconds for the timer"""
        return self.timer_seconds

    def get_difficulty(self):
        """Returns the difficulty level for questions"""
        return self.question_difficulty

    def draw_background(self, screen):
        """Draws the level background"""
        screen.blit(self.background, (0, 0))
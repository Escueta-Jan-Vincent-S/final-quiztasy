import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from .pvp_battle import PVPBattle

class PVP:
    def __init__(self, game_instance):
        """Initialize PVP game mode."""
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.script_dir = game_instance.script_dir
        self.audio_manager = game_instance.audio_manager
        self.level = None  # This will be set when start_battle is called

    def start_battle(self):
        """Start a PVP battle with selected heroes."""
        # No level parameter needed

        # Ensure heroes are selected
        if not hasattr(self.game_instance, 'p1_hero') or not hasattr(self.game_instance, 'p2_hero'):
            print("Error: Heroes not selected!")
            return None

        # Create and run the PVP battle
        battle = PVPBattle(
            self.screen,
            self.script_dir,
            p1_hero=self.game_instance.p1_hero,
            p2_hero=self.game_instance.p2_hero,
            audio_manager=self.audio_manager,
            game_instance=self.game_instance
        )

        # Run the battle and get the result
        result = battle.run()

        # Handle the result
        self.handle_battle_result(result)

        return result

    def handle_battle_result(self, result):
        """Handle the result of the battle."""
        if result == 1:
            print("Player 1 won the battle!")
            # Add any rewards or progress updates here
        elif result == 2:
            print("Player 2 won the battle!")
            # Add any rewards or progress updates here
        else:
            print("Battle was interrupted or ended without a winner.")

        # Return to the main menu or game modes screen
        if hasattr(self.game_instance, 'game_modes'):
            self.game_instance.game_modes.show()
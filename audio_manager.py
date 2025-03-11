import pygame

class AudioManager:
    def __init__(self, music_path, click_sfx_path):
        pygame.mixer.init()
        self.music_path = music_path
        self.click_sfx = None if click_sfx_path is None else pygame.mixer.Sound(click_sfx_path)
        self.is_playing = False

        # Single audio state for both music and sound effects
        self.audio_enabled = True

        # Previous state (for toggling)
        self.prev_music_volume = 1.0
        self.prev_sound_volume = 1.0

    def play_music(self):
        if self.audio_enabled and not self.is_playing:
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            pygame.mixer.music.set_volume(0.3)
            self.is_playing = True

    def stop_music(self):
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False

    def play_sfx(self):
        if self.audio_enabled and self.click_sfx:
            self.click_sfx.play()

    def toggle_audio(self):
        """Toggles all audio (both music and sound effects)."""
        self.audio_enabled = not self.audio_enabled
        if self.audio_enabled:
            # Re-enable all audio
            if not self.is_playing:
                self.play_music()
            else:
                pygame.mixer.music.set_volume(self.prev_music_volume)
            if self.click_sfx:
                self.click_sfx.set_volume(self.prev_sound_volume)
        else:
            # Mute all audio
            pygame.mixer.music.set_volume(0)
            if self.click_sfx:
                self.click_sfx.set_volume(0)

        print(f"Audio Enabled: {self.audio_enabled}")
        return self.audio_enabled
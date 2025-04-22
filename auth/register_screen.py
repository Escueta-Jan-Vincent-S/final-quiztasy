import pygame
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH, FONT_SIZE
from .input_box import InputBox
from ui.button import Button


class RegisterScreen:
    def __init__(self, screen, script_dir, auth_manager, audio_manager=None, on_close_callback=None,
                 on_back_callback=None):
        self.screen = screen
        self.script_dir = script_dir
        self.auth_manager = auth_manager
        self.audio_manager = audio_manager
        self.on_close_callback = on_close_callback
        self.on_back_callback = on_back_callback
        self.visible = False

        # Load assets
        self.load_assets()

        # Create input boxes for registration
        self.input_boxes = {
            'email': InputBox(
                SCREEN_WIDTH // 2 - 340,
                SCREEN_HEIGHT // 2 - 130,
                680,
                60,
                placeholder='Email'
            ),
            'password': InputBox(
                SCREEN_WIDTH // 2 - 340,
                SCREEN_HEIGHT // 2 - 0.25,
                680,
                60,
                placeholder='Password',
                password=True
            ),
            'confirm_password': InputBox(
                SCREEN_WIDTH // 2 - 340,
                SCREEN_HEIGHT // 2 + 125,
                680,
                60,
                placeholder='Confirm Password',
                password=True
            )
        }

        self.register_button = Button(
            SCREEN_WIDTH // 2 - 200,
            SCREEN_HEIGHT // 2 + 275,
            idle_img=self.button_images['register']['normal'],
            hover_img=self.button_images['register']['hover'],
            action=self.register,
            scale=0.5,
            audio_manager=self.audio_manager
        )

        self.back_button = Button(
            SCREEN_WIDTH // 2 + 225,
            SCREEN_HEIGHT // 2 + 275,
            idle_img=self.button_images['back']['normal'],
            hover_img=self.button_images['back']['hover'],
            action=self.back,
            scale=0.5,
            audio_manager=self.audio_manager
        )

        self.close_button = Button(
            x=100,
            y=100,
            idle_img=self.button_images['close']['normal'],
            hover_img=self.button_images['close']['hover'],
            action=self.close,
            scale=0.25,
            audio_manager=self.audio_manager
        )

        # Status message
        self.status_message = ""
        self.status_color = pygame.Color('white')
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZE // 2)

    def load_assets(self):
        # Load panel background
        panel_img_path = os.path.join(self.script_dir, "assets", "images", "login&register", "register_border.png")
        if os.path.exists(panel_img_path):
            self.panel_background = pygame.image.load(panel_img_path).convert_alpha()
            scale = 0.6

            if scale != 1.0:
                original_width = self.panel_background.get_width()
                original_height = self.panel_background.get_height()
                new_size = (int(original_width * scale), int(original_height * scale))
                self.panel_background = pygame.transform.scale(self.panel_background, new_size)

        # Load button images
        img_dir = os.path.join(self.script_dir, "assets", "images", "login&register")
        self.button_images = {
            'register': {
                'normal': os.path.join(img_dir, "register_btn_img.png"),
                'hover': os.path.join(img_dir, "register_btn_hover.png"),
            },
            'back': {
                'normal': os.path.join(img_dir, "back_btn_img.png"),
                'hover': os.path.join(img_dir, "back_btn_hover.png"),
            },
            'close': {
                'normal': os.path.join(img_dir, "close_btn_img.png"),
                'hover': os.path.join(img_dir, "close_btn_hover.png"),
            }
        }

    def register(self):
        email = self.input_boxes['email'].text.strip()
        password = self.input_boxes['password'].text.strip()
        confirm_password = self.input_boxes['confirm_password'].text.strip()

        # Validate inputs
        if not email or not password or not confirm_password:
            self.status_message = "Registration Failed: Please fill in all fields."
            self.status_color = pygame.Color('red')
            return

        if password != confirm_password:
            self.status_message = "Registration Failed: Passwords do not match."
            self.status_color = pygame.Color('red')
            return

        # Attempt to register
        success, message = self.auth_manager.register(email, password)

        if success:
            self.status_message = "Registration successful! You can now log in."
            self.status_color = pygame.Color('green')
            pygame.time.set_timer(pygame.USEREVENT + 2, 1500)  # Close after 1.5 seconds
        else:
            # The AuthManager already checks for duplicate emails and returns "Email already registered"
            # We'll display whatever error message comes from the auth manager
            self.status_message = f"Registration Failed: {message}"
            self.status_color = pygame.Color('red')

    def back(self):
        # Reset input boxes and status message
        for box in self.input_boxes.values():
            box.text = ''
        self.status_message = ""
        self.visible = False

        # Call the back callback if provided
        if self.on_back_callback:
            self.on_back_callback()

    def close(self):
        self.visible = False
        # Reset input boxes and status message
        for box in self.input_boxes.values():
            box.text = ''
        self.status_message = ""

        # Call the callback if provided
        if self.on_close_callback:
            self.on_close_callback()

    def show(self):
        self.visible = True

    def handle_events(self, event):
        if not self.visible:
            return

        # Handle timer event for closing after successful registration
        if event.type == pygame.USEREVENT + 2:
            pygame.time.set_timer(pygame.USEREVENT + 2, 0)  # Stop the timer
            self.back()  # Go back to login screen after successful registration
            return

        # Handle input boxes
        for box in self.input_boxes.values():
            if box.handle_event(event):
                # Enter was pressed in this box
                pass

        # Handle buttons
        self.register_button.update(event)
        self.back_button.update(event)
        self.close_button.update(event)

    def update(self):
        for box in self.input_boxes.values():
            box.update()

    def draw(self):
        if not self.visible:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # RGBA, 180 is the alpha (transparency)
        self.screen.blit(overlay, (0, 0))

        # Draw the panel background
        panel_rect = self.panel_background.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(self.panel_background, panel_rect)

        # Draw the input boxes
        for box in self.input_boxes.values():
            box.draw(self.screen)

        # Draw the buttons
        self.register_button.draw(self.screen)
        self.back_button.draw(self.screen)
        self.close_button.draw(self.screen)

        # Draw status message if any
        if self.status_message:
            status_surf = self.font.render(self.status_message, True, self.status_color)
            self.screen.blit(status_surf, (SCREEN_WIDTH // 2 - status_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 475))
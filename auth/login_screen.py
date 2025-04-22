import pygame
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH, FONT_SIZE
from .input_box import InputBox
from ui.button import Button
from .register_screen import RegisterScreen


class LoginScreen:
    def __init__(self, screen, script_dir, auth_manager, audio_manager=None, on_close_callback=None):
        self.screen = screen
        self.script_dir = script_dir
        self.auth_manager = auth_manager
        self.audio_manager = audio_manager
        self.on_close_callback = on_close_callback
        self.visible = False

        # Load assets
        self.load_assets()

        # Create input boxes for login
        self.input_boxes = {
            'email': InputBox(
                SCREEN_WIDTH // 2 - 340,
                SCREEN_HEIGHT // 2 - 120,
                700,
                60,
                placeholder='Email'
            ),
            'password': InputBox(
                SCREEN_WIDTH // 2 - 340,
                SCREEN_HEIGHT // 2 + 60,
                700,
                60,
                placeholder='Password',
                password=True
            )
        }

        self.login_button = Button(
            SCREEN_WIDTH // 2 - 200,
            SCREEN_HEIGHT // 2 + 275,
            idle_img=self.button_images['login']['normal'],
            hover_img=self.button_images['login']['hover'],
            action=self.login,
            scale=0.5,
            audio_manager=self.audio_manager
        )

        self.register_button = Button(
            SCREEN_WIDTH // 2 + 225,
            SCREEN_HEIGHT // 2 + 275,
            idle_img=self.button_images['register']['normal'],
            hover_img=self.button_images['register']['hover'],
            action=self.show_register,
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

        # Create register screen
        self.register_screen = RegisterScreen(
            screen=self.screen,
            script_dir=self.script_dir,
            auth_manager=self.auth_manager,
            audio_manager=self.audio_manager,
            on_close_callback=self.on_close_callback,
            on_back_callback=self.show_login
        )

    def load_assets(self):
        # Load panel background
        panel_img_path = os.path.join(self.script_dir, "assets", "images", "login&register", "login_border.png")
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
            'login': {
                'normal': os.path.join(img_dir, "login_btn_img.png"),
                'hover': os.path.join(img_dir, "login_btn_hover.png"),
            },
            'register': {
                'normal': os.path.join(img_dir, "register_btn_img.png"),
                'hover': os.path.join(img_dir, "register_btn_hover.png"),
            },
            'close': {
                'normal': os.path.join(img_dir, "close_btn_img.png"),
                'hover': os.path.join(img_dir, "close_btn_hover.png"),
            }
        }

    def login(self):
        email = self.input_boxes['email'].text.strip()
        password = self.input_boxes['password'].text.strip()

        if not email or not password:
            self.status_message = "Login Failed: Please fill in both Email and Password."
            self.status_color = pygame.Color('red')
            return
        success, message = self.auth_manager.login(email, password)
        if success:
            self.status_message = "Login successful!"
            self.status_color = pygame.Color('green')
            pygame.time.set_timer(pygame.USEREVENT + 1, 1500)  # Close after 1.5 seconds
        else:
            self.status_message = "Login Failed: User not found or incorrect credentials."
            self.status_color = pygame.Color('red')

    def show_register(self):
        # Hide login screen and show register screen
        self.visible = False
        self.register_screen.show()
        self.status_message = ""

    def show_login(self):
        # Show login screen (called from register screen when going back)
        self.visible = True

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
        # First check if register screen is visible
        if self.register_screen.visible:
            self.register_screen.handle_events(event)
            return

        if not self.visible:
            return

        # Handle timer event for closing after successful login
        if event.type == pygame.USEREVENT + 1:
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Stop the timer
            self.close()
            return

        # Handle input boxes
        for box in self.input_boxes.values():
            if box.handle_event(event):
                # Enter was pressed in this box
                pass

        # Handle buttons
        self.login_button.update(event)
        self.register_button.update(event)
        self.close_button.update(event)

    def update(self):
        if self.register_screen.visible:
            self.register_screen.update()
            return

        if self.visible:
            for box in self.input_boxes.values():
                box.update()

    def draw(self):
        # First check if register screen is visible
        if self.register_screen.visible:
            self.register_screen.draw()
            return

        if not self.visible:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # RGBA, 180 is the alpha (transparency)
        self.screen.blit(overlay, (0, 0))

        # Draw the panel background
        panel_rect = self.panel_background.get_rect(center=(SCREEN_WIDTH // 2 + 65, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(self.panel_background, panel_rect)

        # Draw the input boxes
        for box in self.input_boxes.values():
            box.draw(self.screen)

        # Draw the buttons
        self.login_button.draw(self.screen)
        self.register_button.draw(self.screen)
        self.close_button.draw(self.screen)

        # Draw status message if any
        if self.status_message:
            status_surf = self.font.render(self.status_message, True, self.status_color)
            self.screen.blit(status_surf, (SCREEN_WIDTH // 2 - status_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 475))
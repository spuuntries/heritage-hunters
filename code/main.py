import pygame, sys
from settings import *
from level import Level
from button import Button


class Game:
    def __init__(self):
        self.state = "menu"

        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        pygame.display.set_caption("Zelda")
        self.clock = pygame.time.Clock()
        self.level = Level()

        # sound
        # main_sound = pygame.mixer.Sound("../audio/main.ogg")
        # main_sound.set_volume(0.5)
        # main_sound.play(loops=-1)

    def get_font(self, size):
        return pygame.font.Font("../graphics/menu/font.ttf", size)

    def run(self):
        while self.state == "game":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.level.toggle_menu()
            self.screen.fill(WATER_COLOR)
            self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)

    def main_menu(self):
        while self.state == "menu":
            MENU_MOUSE_POS = pygame.mouse.get_pos()

            MENU_TEXT = self.get_font(100).render("MAIN MENU", True, "#b68f40")
            MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

            PLAY_BUTTON = Button(
                image=pygame.image.load("../graphics/menu/Play Rect.png"),
                pos=(640, 250),
                text_input="PLAY",
                font=self.get_font(75),
                base_color="#d7fcd4",
                hovering_color="White",
            )
            # OPTIONS_BUTTON = Button(image=pygame.image.load("../graphics/menu/Options Rect.png"), pos=(640, 400),
            #                     text_input="OPTIONS", font=self.get_font(75), base_color="#d7fcd4", hovering_color="White")
            QUIT_BUTTON = Button(
                image=pygame.image.load("../graphics/menu/Quit Rect.png"),
                pos=(640, 550),
                text_input="QUIT",
                font=self.get_font(75),
                base_color="#d7fcd4",
                hovering_color="White",
            )

            self.screen.blit(MENU_TEXT, MENU_RECT)

            for button in [PLAY_BUTTON, QUIT_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                        self.state = "game"
                        self.run()
                    # if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    #     options()
                    if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                        pygame.quit()
                        sys.exit()

            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.main_menu()

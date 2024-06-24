import pygame, sys
from settings import *
from level import Level
from button import Button


class Game:
    def __init__(self):
        self.state = "input_name"

        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        pygame.display.set_caption("Zelda")
        self.clock = pygame.time.Clock()
        self.level = Level()

        # input name setup
        self.user_name = ""
        self.font = pygame.font.Font(None, 50)
        self.input_box = pygame.Rect(400, 300, 400, 50)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.active = False

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

    def input_name(self):
        while self.state == "input_name":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.input_box.collidepoint(event.pos):
                        self.active = not self.active
                    else:
                        self.active = False
                    self.color = self.color_active if self.active else self.color_inactive
                if event.type == pygame.KEYDOWN:
                    if self.active:
                        if event.key == pygame.K_RETURN:
                            # generate pass nya nanti di sini kah?
                            self.state = "menu"
                        elif event.key == pygame.K_BACKSPACE:
                            self.user_name = self.user_name[:-1]
                        else:
                            self.user_name += event.unicode

            self.screen.fill((30, 30, 30))
            txt_surface = self.font.render(self.user_name, True, self.color)
            width = max(400, txt_surface.get_width() + 10)
            self.input_box.w = width
            self.screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))
            pygame.draw.rect(self.screen, self.color, self.input_box, 2)
            pygame.display.flip()
            self.clock.tick(30)

    def main_menu(self):
        while self.state == "menu":
            MENU_MOUSE_POS = pygame.mouse.get_pos()

            self.screen.fill("black")

            MENU_TEXT = self.get_font(100).render(f"Hello {self.user_name}", True, "#b68f40")
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
    game.input_name()
    game.main_menu()

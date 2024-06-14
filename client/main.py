import pygame, sys
from settings import *
from level import Level
from generate import generate_maze


class Game:
    def __init__(self):

        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        pygame.display.set_caption("Zelda")
        self.clock = pygame.time.Clock()

        self.players = ["461", "462"]
        self.level = Level(
            list(
                map(
                    lambda row: list(map(str, row)),
                    generate_maze(39, 39, list(map(int, self.players))),
                )
            ),
            self.players,
        )

        # sound
        # main_sound = pygame.mixer.Sound("../audio/main.ogg")
        # main_sound.set_volume(0.5)
        # main_sound.play(loops=-1)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.level.toggle_menu()

            self.screen.fill("#000000")
            self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()

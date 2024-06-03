import pygame

pygame.init()
font = pygame.font.Font(None, 30)


def debug(info, y=10, x=10):
    display_surface = pygame.display.get_surface()

    # Assuming you know the size of the debug text area, clear it by filling it with the background color
    background_color = (0, 0, 0)  # Change this to match your actual background color
    debug_text_size = font.size(str(info))  # Get the size of the current debug text
    pygame.draw.rect(display_surface, background_color, (x, y, *debug_text_size))

    # Now draw the new debug text
    debug_surf = font.render(str(info), True, "White")
    debug_rect = debug_surf.get_rect(topleft=(x, y))
    pygame.draw.rect(display_surface, "Black", debug_rect)
    display_surface.blit(debug_surf, debug_rect)

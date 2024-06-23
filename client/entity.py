import pygame
from math import sin
from debug import debug
from settings import *


class Entity(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.frame_index = 0
        self.animation_speed = 0.15
        self.direction = pygame.math.Vector2()

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Calculate the target position based on the current position and direction
        target_x = self.hitbox.x + self.direction.x * speed
        target_y = self.hitbox.y + self.direction.y * speed

        # Round the target position to the nearest multiple of 64 (assuming 64x64 grid)
        target_x = round(target_x / 64) * 64
        target_y = round(target_y / 64) * 64

        # Check for collisions at the target position
        target_hitbox = self.hitbox.copy()
        prev_hitbox = self.hitbox.copy()
        target_hitbox.x = target_x
        target_hitbox.y = target_y

        # Horizontal collision handling
        for sprite in self.obstacle_sprites.sprites():
            if sprite.hitbox.collidepoint(target_hitbox.x, target_hitbox.y):
                if self.direction.x > 0:  # moving right
                    target_hitbox.right = sprite.hitbox.left
                if self.direction.x < 0:  # moving left
                    target_hitbox.left = sprite.hitbox.right
                self.direction.x = 0  # stop horizontal movement

        # Vertical collision handling
        for sprite in self.obstacle_sprites.sprites():
            if sprite.hitbox.collidepoint(target_hitbox.x, target_hitbox.y):
                if self.direction.y > 0:  # moving down
                    target_hitbox.bottom = sprite.hitbox.top
                if self.direction.y < 0:  # moving up
                    target_hitbox.top = sprite.hitbox.bottom
                self.direction.y = 0  # stop vertical movement

        for sprite in self.obstacle_sprites.sprites():
            if sprite.hitbox.collidepoint(target_hitbox.x, target_hitbox.y):
                # Move the player back to the previous position
                self.hitbox.x = prev_hitbox.x
                self.hitbox.y = prev_hitbox.y
                break
            else:
                # Update the hitbox position to the target position if no collision
                self.hitbox.x = target_hitbox.x
                self.hitbox.y = target_hitbox.y

        self.rect.center = self.hitbox.center

    def wave_value(self):
        value = sin(pygame.time.get_ticks())
        if value >= 0:
            return 255
        else:
            return 0

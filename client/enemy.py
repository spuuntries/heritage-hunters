from os import path
from typing import Any
import pygame
import pathing
from settings import *
from entity import Entity
from support import *
import math


class Enemy(Entity):
    def __init__(
        self,
        monster_name,
        pos,
        groups,
        obstacle_sprites: Any,
        damage_player,
        trigger_death_particles,
        add_exp,
        attackable_sprites,
    ):

        # general setup
        super().__init__(groups)
        self.sprite_type = "enemy"

        # graphics setup
        self.import_graphics(monster_name)
        self.status = "idle"
        self.image = self.animations[self.status][self.frame_index]

        # movement
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        if monster_name == "raccoon":
            self.hitbox = self.rect.inflate(-176, -186)
        self.obstacle_sprites: list[Any] = obstacle_sprites
        self.attackable_sprites = attackable_sprites
        self.player = None

        # stats
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info["health"]
        self.exp = monster_info["exp"]
        self.speed = 64
        self.attack_damage = monster_info["damage"]
        self.resistance = monster_info["resistance"]
        self.attack_radius = monster_info["attack_radius"]
        self.notice_radius = monster_info["notice_radius"]
        self.attack_type = monster_info["attack_type"]

        # player interaction
        self.can_attack = True
        self.attack_time: int = None
        self.attack_cooldown = 400
        self.damage_player = damage_player
        self.trigger_death_particles = trigger_death_particles
        self.add_exp = add_exp

        # invincibility timer
        self.vulnerable = True
        self.hit_time: int = None
        self.invincibility_duration = 300

        # sounds
        self.death_sound = pygame.mixer.Sound("../audio/death.wav")
        self.hit_sound = pygame.mixer.Sound("../audio/hit.wav")
        self.attack_sound = pygame.mixer.Sound(monster_info["attack_sound"])
        self.death_sound.set_volume(0.6)
        self.hit_sound.set_volume(0.6)
        self.attack_sound.set_volume(0.6)

        self.last_movement_update_time = pygame.time.get_ticks()
        self.movement_delay = (
            max(map(lambda m: m["speed"], monster_data.values()))
            / monster_info["speed"]
        ) * 350
        # self.movement_delay = 400
        self.prev_move = None

    def import_graphics(self, name):
        self.animations = {"idle": [], "move": [], "attack": []}
        main_path = f"../graphics/monsters/{name}/"
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return (distance, direction)

    def get_direction_vector(self, a, b, x, y):
        # Calculate the differences in x and y coordinates
        dx = x - a
        dy = y - b

        # Create a Vector2 object with the calculated differences
        direction = pygame.math.Vector2(dx, dy)

        # Normalize the vector
        if direction.length() != 0:
            direction.normalize_ip()

        return direction

    def get_status(self, player):
        distance = self.get_player_distance_direction(player)[0]

        if distance <= self.attack_radius and self.can_attack:
            if self.status != "attack":
                self.frame_index = 0
            self.status = "attack"
        elif distance <= self.notice_radius:
            self.status = "move"
        else:
            self.status = "idle"

    def actions(self, player):
        if self.status == "attack":
            self.attack_time = pygame.time.get_ticks()
            self.damage_player(self.attack_damage, self.attack_type)
            self.attack_sound.play()
        else:
            self.direction = pygame.math.Vector2()

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.status == "attack":
                self.can_attack = False
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True

        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

    def get_damage(self, player, attack_type):
        if self.vulnerable:
            self.hit_sound.play()
            self.direction = self.get_player_distance_direction(player)[1]
            if attack_type == "weapon":
                self.health -= player.get_full_weapon_damage()
            else:
                self.health -= player.get_full_magic_damage()
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def check_death(self):
        if self.health <= 0:
            self.kill()
            self.trigger_death_particles(self.rect.center, self.monster_name)
            self.add_exp(self.exp)
            self.death_sound.play()

    def hit_reaction(self):
        if not self.vulnerable:
            self.direction *= -self.resistance

    def update(self):
        self.hit_reaction()
        current_time = pygame.time.get_ticks()

        if current_time - self.last_movement_update_time >= self.movement_delay:
            self.last_movement_update_time = current_time
            g_values = {}
            if self.player and self.status == "move":
                if self.monster_name == "bamboo":
                    path = pathing.find_path_maximizing_distance(
                        self.rect.center,
                        self.player.rect.center,
                        list(map(lambda s: s.rect.center, self.obstacle_sprites)),
                        TILESIZE,
                        1,
                        self.player.status,
                    )
                else:
                    path = pathing.adaptive_a_star(
                        self.rect.center,
                        self.player.rect.center,
                        list(map(lambda s: s.rect.center, self.obstacle_sprites)),
                        TILESIZE,
                        g_values,
                        self.prev_move,
                    )
                if path:
                    self.direction = self.get_direction_vector(
                        self.rect.center[0],
                        self.rect.center[1],
                        path[0][0],
                        path[0][1],
                    )
                    self.prev_move = path[0]
                    print(path)
                    self.move(self.speed)
                    print(self.direction)
        self.animate()
        self.cooldowns()
        self.check_death()

    def enemy_update(self, player):
        self.player = player
        self.get_status(player)
        self.actions(player)
from enum import Enum
import pygame
import math


class CarAction(Enum):
    LEFT = 0
    RIGHT = 1
    BREAK = 2
    ACCELERATE = 3
    IDLE = 4


class Car:

    def __init__(self):
        self.sprite = pygame.image.load('./imgs/green.png')
        self.acceleration = 0.5
        self.break_strength = 0.8
        self.max_speed = 10

        self.position = [620, 675]
        self.angle = -90
        self.speed = 0
        self.angular_speed = 30

        self.is_alive = True
        self.has_completed = False

        self.radar_count = 10
        self.max_radar_length = 300
        self.radar_dists = []
        for i in range(0, self.radar_count):
            self.radar_dists.append(0)
        self.radar_end_positions = []

        self.distance = 0

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.sprite, self.angle)
        new_rect = rotated_image.get_rect(center=self.position)
        screen.blit(rotated_image, new_rect)
        if self.is_alive:
            self.draw_radar(screen)

    def draw_radar(self, screen):
        for radar in self.radar_end_positions:
            radar_end = radar
            pygame.draw.line(screen, (0, 255, 0), self.position, radar_end, 1)
            pygame.draw.circle(screen, (0, 255, 0), radar_end, 5)

    def is_colliding(self, track_mask):
        rotated_sprite = pygame.transform.rotate(self.sprite, self.angle)
        draw_rect = rotated_sprite.get_rect(center=self.position)
        car_mask = pygame.mask.from_surface(rotated_sprite)
        return track_mask.overlap(car_mask, draw_rect.topleft)

    def check_radars(self, map_mask):
        radar_angle_offset = self.angle
        self.radar_end_positions.clear()
        self.radar_dists.clear()

        for i in range(0, self.radar_count):
            length = 0
            x = int(self.position[0] + math.cos(math.radians(360 - radar_angle_offset)))
            y = int(self.position[1] + math.sin(math.radians(360 - radar_angle_offset)))

            while not map_mask.get_at((x, y)) == 1 and length < self.max_radar_length:
                length = length + 1
                x = int(self.position[0] + math.cos(math.radians(360 - radar_angle_offset)) * length)
                y = int(self.position[1] + math.sin(math.radians(360 - radar_angle_offset)) * length)

            dist = int(math.sqrt(math.pow(x - self.position[0], 2) + math.pow(y - self.position[1], 2)))
            self.radar_end_positions.append((x, y))
            self.radar_dists.append(dist)

            radar_angle_offset += 180 / (self.radar_count - 1)

    def rotate(self, left=False, right=False ):
        if left:
            self.angle += self.angular_speed
        elif right:
            self.angle -= self.angular_speed

    def add_speed(self):
        self.speed = min((self.speed + self.acceleration), self.max_speed)

    def reduce_speed(self):
        self.speed = max((self.speed - self.acceleration), 0)

    def update(self, choice):
        action = CarAction(choice)
        if action == CarAction.ACCELERATE:
            self.add_speed()
        if action == CarAction.LEFT:
            self.rotate(left=True)
        if action == CarAction.RIGHT:
            self.rotate(right=True)
        if action == CarAction.BREAK:
            self.reduce_speed()

        self.distance += self.speed

        self.position[1] -= math.cos(math.radians(self.angle)) * self.speed
        self.position[0] -= math.sin(math.radians(self.angle)) * self.speed

    def get_state(self):
        state = []
        for dist in self.radar_dists:
            state.append(dist / self.max_radar_length)

        state.append(self.speed / self.max_speed)
        return state

    def get_fitness(self, total_time):
        if total_time == 0:
            return 0
        return self.distance - total_time * 0.01

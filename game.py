import math
import sys

import neat
import pygame

WIDTH = 1920
HEIGHT = 1080

BORDER_COLOR = (255, 255, 255, 255)  # Color To Crash on Hit

def blit_rotate_center(screen, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
    screen.blit(rotated_image, new_rect.topleft)


class Car:

    def __init__(self):
        self.sprite = pygame.image.load('./imgs/green.png')
        self.sprite = pygame.transform.scale_by(self.sprite, 2)
        self.acceleration = 0.1
        self.break_strenght = 0.8
        self.max_speed = 10

        self.position = [830, 900]
        self.angle = -90
        self.speed = 0
        self.angular_speed = 5

        self.radars = []
        self.drawing_radars = []

        self.alive = True

        self.distance = 0
        self.time = 0

    def draw(self, screen):
        blit_rotate_center(screen, self.sprite, self.position, self.angle)
        self.draw_radar(screen)

    def draw_radar(self, screen):
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    def is_colliding(self, track_mask):
        car_mask = pygame.mask.from_surface(self.sprite)
        offset = (self.position[0], self.position[1])
        return track_mask.overlap(car_mask, offset)


    def check_radar(self, degree, game_map):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # While We Don't Hit BORDER_COLOR AND length < 300 (just a max) -> go further and further
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            length = length + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # Calculate Distance To Border And Append To Radars List
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.angular_speed
        elif right:
            self.angle -= self.angular_speed

    def add_speed(self):
        self.speed = min(self.speed + self.acceleration, self.max_speed)

    def reduce_speed(self):
        self.speed = max(self.speed - self.acceleration, 0)

    def update(self, game_map):
        self.distance += self.speed
        self.time += 1

        self.position[1] -= math.cos(math.radians(self.angle)) * self.speed
        self.position[0] -= math.sin(math.radians(self.angle)) * self.speed

        # for d in range(-90, 120, 45):
        # self.check_radar(d, game_map)

    def get_data(self):
        # Get Distances To Border
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    def is_alive(self):
        return self.alive

    def get_reward(self):
        return self.distance / (Car.SIZE_X / 2)


def poll_events(car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_UP]:
        car.add_speed()
        moved = True
    if keys[pygame.K_LEFT]:
        car.rotate(left=True)
    if keys[pygame.K_RIGHT]:
        car.rotate(right=True)

    if not moved:
        car.reduce_speed()


# Main Code
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

clock = pygame.time.Clock()

game_map = pygame.image.load('./imgs/map.png').convert()
MAP_MASK = pygame.mask.from_surface(game_map)

car = Car()

counter = 0

while True:
    # Exit On Quit Event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)

    poll_events(car)
    car.update(game_map)

    if car.is_colliding(MAP_MASK):
        car = Car()

    screen.blit(game_map, (0, 0))
    car.draw(screen)

    pygame.display.flip()
    clock.tick(60)

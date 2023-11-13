import math
import sys
from enum import Enum
import pygame

WIDTH = 1366
HEIGHT = 768


def blit_rotate_center(screen, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=top_left)
    screen.blit(rotated_image, new_rect)


class CarAction(Enum):
    LEFT = 0
    RIGHT = 1
    BREAK = 2
    ACCELERATE = 3
    IDLE = 4


class Car:

    def __init__(self):
        self.sprite = pygame.image.load('./imgs/green.png')
        self.acceleration = 0.1
        self.break_strength = 0.8
        self.max_speed = 10

        self.position = [620, 675]
        self.angle = -90
        self.speed = 0
        self.angular_speed = 2.5

        self.action = CarAction.IDLE

        self.radar_count = 5
        self.radar_dists = []
        self.radar_end_positions = []

        self.distance = 0
        self.time = 0

    def draw(self, screen):
        blit_rotate_center(screen, self.sprite, self.position, self.angle)
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

            while not map_mask.get_at((x, y)) == 1 and length < 300:
                length = length + 1
                x = int(self.position[0] + math.cos(math.radians(360 - radar_angle_offset)) * length)
                y = int(self.position[1] + math.sin(math.radians(360 - radar_angle_offset)) * length)

            dist = int(math.sqrt(math.pow(x - self.position[0], 2) + math.pow(y - self.position[1], 2)))
            self.radar_end_positions.append((x, y))
            self.radar_dists.append(dist)

            radar_angle_offset += 180 / (self.radar_count - 1)

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.angular_speed
        elif right:
            self.angle -= self.angular_speed

    def add_speed(self):
        self.speed = min(self.speed + self.acceleration, self.max_speed)

    def reduce_speed(self):
        self.speed = max(self.speed - self.acceleration, 0)

    def active_break(self):
        self.speed = max(self.speed - self.break_strength, 0)

    def update(self, delta_time):
        self.distance += self.speed
        self.time += delta_time

        self.position[1] -= math.cos(math.radians(self.angle)) * self.speed
        self.position[0] -= math.sin(math.radians(self.angle)) * self.speed

    def get_score(self):
        if self.time == 0:
            return 0
        return self.distance / (self.time / 1000)


def poll_events(car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_UP]:
        car.add_speed()
        car.action = CarAction.ACCELERATE
        moved = True
    if keys[pygame.K_DOWN]:
        car.action = CarAction.BREAK
        car.active_break()
    if keys[pygame.K_LEFT]:
        car.action = CarAction.LEFT
        car.rotate(left=True)
    if keys[pygame.K_RIGHT]:
        car.action = CarAction.RIGHT
        car.rotate(right=True)

    if not keys[pygame.K_RIGHT] and not keys[pygame.K_DOWN] and not keys[pygame.K_LEFT] and not keys[pygame.K_UP]:
        car.action = CarAction.IDLE

    if not moved:
        car.reduce_speed()


def print_dists(screen, dists):
    title_font = pygame.font.Font("freesansbold.ttf", 15)
    text_surface = title_font.render("Radar", True, (0, 255, 0, 255))
    screen.blit(text_surface, (20, 20))

    text_font = pygame.font.Font("freesansbold.ttf", 10)
    y = 35
    count = 1
    for dist in dists:
        text_surface = text_font.render("r" + str(count) + ": " + str(dist), True, (0, 0, 0, 255))
        screen.blit(text_surface, (20, y))
        y += 10
        count += 1


def print_states(screen, car):
    tittle_font = pygame.font.Font("freesansbold.ttf", 15)
    text_surface = tittle_font.render("States", True, (255, 0, 0, 255))
    screen.blit(text_surface, (100, 20))

    text_font = pygame.font.Font("freesansbold.ttf", 10)
    text_surface = text_font.render("Action: " + car.action.name, True, (0, 0, 0, 255))
    screen.blit(text_surface, (100, 35))

    text_surface = text_font.render("Speed: " + "{:.2f}".format(car.speed), True, (0, 0, 0, 255))
    screen.blit(text_surface, (100, 45))

    text_surface = text_font.render("Score: " + "{:.2f}".format(car.get_score()), True, (0, 0, 0, 255))
    screen.blit(text_surface, (100, 55))


# Main Code
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()

game_map = pygame.image.load('./imgs/map1.png').convert()
game_map = pygame.transform.scale(game_map, (1366, 768))

MAP_MASK = game_map.copy()
MAP_MASK.set_colorkey((255, 255, 255))
MAP_MASK = pygame.mask.from_surface(MAP_MASK)
MAP_MASK.invert()

FINISH_MASK = game_map.copy()
FINISH_MASK.set_colorkey((0, 0, 255))
FINISH_MASK = pygame.mask.from_surface(FINISH_MASK)
FINISH_MASK.invert()

car = Car()
is_game_running = True

counter = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)

    if (is_game_running):
        poll_events(car)
        car.update(clock.get_time())
        car.check_radars(MAP_MASK)

        if car.is_colliding(MAP_MASK):
            car = Car()

        if car.is_colliding(FINISH_MASK):
            is_game_running = False

    screen.blit(game_map, (0, 0))
    car.draw(screen)

    print_dists(screen, car.radar_dists)
    print_states(screen, car)

    pygame.display.flip()
    clock.tick(60)

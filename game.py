import pygame
from collections import deque


class Game:
    WIDTH = 1366
    HEIGHT = 768
    GENERATION = 0

    def __init__(self, cars, genomes):
        pygame.init()
        Game.GENERATION += 1

        self.total_time = 0
        self.cars = cars
        self.genomes = genomes
        self.screen = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))

        self.clock = pygame.time.Clock()
        self.MAP = pygame.transform.scale(pygame.image.load("./imgs/map1.png").convert(), (Game.WIDTH, Game.HEIGHT))

        self.TRACK_MASK = self.MAP.copy()
        self.TRACK_MASK.set_colorkey((255, 255, 255))
        self.TRACK_MASK = pygame.mask.from_surface(self.TRACK_MASK)

        self.COLLISION_MASK = self.TRACK_MASK.copy()
        self.COLLISION_MASK.invert()
        self.dt = 0

        self.FINISH_MASK = self.MAP.copy()
        self.FINISH_MASK.set_colorkey((0, 0, 255))
        self.FINISH_MASK = pygame.mask.from_surface(self.FINISH_MASK)
        self.FINISH_MASK.invert()

        self.collision_mask = self.COLLISION_MASK.copy

        self.FLOODFILL_TILE_SIZE = 20
        self.FLOODFILL_MASK = self.TRACK_MASK.copy()
        self.SQUARE_MASK = pygame.mask.Mask((self.FLOODFILL_TILE_SIZE, self.FLOODFILL_TILE_SIZE), True)

        self.queue = deque()
        self.queue.append((550, 650))

    def check_collisions(self, car, i):
        if not car.is_alive or car.has_completed:
            return

        car.check_radars(self.COLLISION_MASK)
        if car.is_colliding(self.COLLISION_MASK):
            car.is_alive = False
        if car.is_colliding(self.FINISH_MASK):
            self.genomes[i][1].fitness += 200000
            car.has_completed = True

    def tick(self):
        self.screen.blit(self.MAP, (0, 0))

        tittle_font = pygame.font.Font("freesansbold.ttf", 15)

        for i, car in enumerate(self.cars):
            text_surface = tittle_font.render("{:.2f}".format(self.genomes[i][1].fitness), True, (255, 0, 0, 255))
            self.screen.blit(text_surface, (car.position[0] - 20, car.position[1] - 40))
            car.draw(self.screen)

        wave = self.COLLISION_MASK.overlap_mask(self.TRACK_MASK, (0,0))
        self.screen.blit(wave.to_surface(setcolor=(255,255,0), unsetcolor=(0,0,0,0)), (0, 0))
        # self.screen.blit(self.COLLISION_MASK.to_surface(), (0, 0))
        self.print_generation()
        pygame.display.flip()

        self.dt = self.clock.tick(60)
        self.total_time += self.dt

    def find_neighbors(self, element):
        possible_neighbors = [
            (element[0] + self.FLOODFILL_TILE_SIZE, element[1]),
            (element[0] - self.FLOODFILL_TILE_SIZE, element[1]),
            (element[0], element[1] + self.FLOODFILL_TILE_SIZE),
            (element[0], element[1] - self.FLOODFILL_TILE_SIZE),
        ]

        size_x, size_y = self.COLLISION_MASK.get_size()
        found = []
        for possible_neighbor in possible_neighbors:
            if 0 <= possible_neighbor[0] <= size_x and 0 <= possible_neighbor[1] <= size_y:
                if self.FLOODFILL_MASK.overlap(self.SQUARE_MASK, possible_neighbor):
                    found.append(possible_neighbor)

        return found

    def flood_fill(self):
        if self.total_time < 500 or len(self.queue) <= 0:
            return

        element = self.queue.popleft()
        neighbors = self.find_neighbors(element)
        for neighbor in neighbors:
            self.FLOODFILL_MASK.erase(self.SQUARE_MASK, neighbor)
            self.queue.append(neighbor)

        self.COLLISION_MASK = self.FLOODFILL_MASK.copy()
        self.COLLISION_MASK.invert()

    def print_dists(self, dists):
        title_font = pygame.font.Font("freesansbold.ttf", 15)
        text_surface = title_font.render("Radar", True, (0, 255, 0, 255))
        self.screen.blit(text_surface, (20, 20))

        text_font = pygame.font.Font("freesansbold.ttf", 10)
        y = 35
        count = 1
        for dist in dists:
            text_surface = text_font.render("r" + str(count) + ": " + str(dist), True, (0, 0, 0, 255))
            self.screen.blit(text_surface, (20, y))
            y += 10
            count += 1

    def print_generation(self):
        tittle_font = pygame.font.Font("freesansbold.ttf", 25)
        text_surface = tittle_font.render("Generation " + str(Game.GENERATION), True, (255, 0 , 0, 255))
        rect = text_surface.get_rect()
        self.screen.blit(text_surface, ((Game.WIDTH - rect.width / 2) / 2, 20))

    def print_states(self, car):
        tittle_font = pygame.font.Font("freesansbold.ttf", 15)
        text_surface = tittle_font.render("States", True, (255, 0, 0, 255))
        self.screen.blit(text_surface, (100, 20))

        text_font = pygame.font.Font("freesansbold.ttf", 10)
        text_surface = text_font.render("Action: " + car.action.name, True, (0, 0, 0, 255))
        self.screen.blit(text_surface, (100, 35))

        text_surface = text_font.render("Speed: " + "{:.2f}".format(car.speed), True, (0, 0, 0, 255))
        self.screen.blit(text_surface, (100, 45))

        text_surface = text_font.render("Score: " + "{:.2f}".format(car.get_score()), True, (0, 0, 0, 255))
        self.screen.blit(text_surface, (100, 55))

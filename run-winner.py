import pickle
import neat
import pygame
import visualize
from game import Game
from car import Car
import sys
class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

with open('imgs/Train3/winner', 'rb') as f:
    c = pickle.load(f)

print("Loaded genome")
print(c)

CONFIG_PATH = "./config.txt"
neat_config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                 neat.DefaultStagnation, CONFIG_PATH)
population = neat.Population(neat_config)
stats = neat.StatisticsReporter()
population.add_reporter(stats)
population.add_reporter(neat.StdOutReporter(True))

net = neat.nn.FeedForwardNetwork.create(c, neat_config)

cars = []
genomes = [[net, dotdict(fitness = 0)]]
print(genomes[0][1].fitness)
print(genomes)
cars.append(Car())
game = Game(cars, genomes, "map5")
count = 0

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)

    if count < 2000:
        game.clock.tick(60)
        count += game.clock.get_time()
        continue

    game.flood_fill()

    remaining_cars = 0
    for i, car in enumerate(cars):
        if car.is_alive and not car.has_completed:
            remaining_cars += 1
            output = net.activate(car.get_state())
            car.update(output.index(max(output)))
            game.check_collisions(car, i)

    if remaining_cars == 0:
        break

    game.tick()
    if pygame.key.get_pressed()[pygame.K_t]:
        raise Exception("Forced stop")

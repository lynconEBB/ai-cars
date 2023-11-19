import sys
from collections import deque

import neat
import pygame
from game import Game
from car import Car
from car import CarAction


def run_simulation(genomes, config):
    # Create neural networks
    nets = []
    cars = []

    count = 0
    for id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

        cars.append(Car())
        count += 1

    print(count)

    # Create game instance
    game = Game(cars, genomes)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        game.flood_fill()

        remaining_cars = 0
        for i, car in enumerate(cars):
            if car.is_alive and not car.has_completed:
                remaining_cars += 1
                output = nets[i].activate(car.get_state())
                car.update(output.index(max(output)), game.clock.get_time())
                game.check_collisions(car, i)
                genomes[i][1].fitness += car.get_fitness()

        if remaining_cars == 0:
            break

        game.tick()


CONFIG_PATH = "./config.txt"
neat_config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                 neat.DefaultStagnation, CONFIG_PATH)
population = neat.Population(neat_config)
population.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
population.add_reporter(stats)

population.run(run_simulation, 1000)

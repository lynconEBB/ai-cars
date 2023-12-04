import sys
import pickle

import neat
import visualize
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
                car.update(output.index(max(output)))
                genomes[i][1].fitness = car.get_fitness(game.total_time)
                game.check_collisions(car, i)

        if remaining_cars == 0:
            break

        game.tick()
        if pygame.key.get_pressed()[pygame.K_t]:
            raise Exception("Forced stop")



CONFIG_PATH = "./config.txt"
neat_config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                 neat.DefaultStagnation, CONFIG_PATH)
population = neat.Population(neat_config)
stats = neat.StatisticsReporter()
population.add_reporter(stats)
population.add_reporter(neat.StdOutReporter(True))

# evaluator = neat.ParallelEvaluator(multiprocessing.cpu_count(), run_simulation)

try:
    winner = population.run(run_simulation, 1000)
except Exception as e:
    pass

visualize.plot_stats(stats, True, True, "fitness.svg")
visualize.plot_species(stats, True, "species.svg")

with open('winner', 'wb') as f:
    pickle.dump(winner, f)

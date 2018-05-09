import os
import neat
from grid import Grid

RADIUS = 5
NUM_GRIDS = 30
NUM_GENERATIONS = 300
NUM_PUMPJACKS = 10
SIZE_OF_GRID = 32

START_WORST_COUNT = 5
END_WORST_COUNT = 3
WORST_COUNT_STEP_GENERATIONS = 50
WORST_COUNT_STEP_SIZE = -1

gen = 0
worst_count = START_WORST_COUNT
def eval_genomes(genomes, config):
  global gen, worst_count
  best = -10
  best_genome = None
  average = 0.0
  grids = []
  for i in range(0, 20):
    grids.append(Grid(SIZE_OF_GRID, SIZE_OF_GRID, NUM_PUMPJACKS))
  for genome_id, genome in genomes:
    genome.fitness = 1000000
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    all_worst = []
    for grid in grids:
      grid.reset()
      for x in range(0, grid.width - 3):
        for y in range(0, grid.height - 3):
          input = grid.getInput(x + 1, y + 1, RADIUS)
          if input is False:
            continue
          output = net.activate(input)
          if output[0] >= 0.5:
            grid.placeBeacon(x, y)
      
      fitness = grid.getFitness()
      if len(all_worst) < worst_count:
        all_worst.append(fitness)
      else:
        for i in range(0, len(all_worst)):
          if fitness < all_worst[i]:
            all_worst[i] = fitness
            break
      average += float(fitness) / NUM_GRIDS
    
    genome.fitness = 0
    for worst in all_worst:
      genome.fitness += float(worst)/worst_count
    
    if fitness > best:
      best_genome = genome
    best = max(best, fitness)
  
  print("Gen: "+str(gen)+", Best: "+str(best)+", Average: "+str(average / len(genomes)))
  if gen % 10 == 0:
    run_test(best_genome, config)
  gen += 1
  if gen % WORST_COUNT_CHANGE_GENERATIONS == 0:
    if worst_count != END_WORST_COUNT:
      worst_count = worst_count + WORST_COUNT_STEP_SIZE

def run_test(genome, config):
  net = neat.nn.FeedForwardNetwork.create(genome, config)
  grid = Grid(SIZE_OF_GRID, SIZE_OF_GRID, NUM_PUMPJACKS)
  for x in range(0, grid.width - 3):
    for y in range(0, grid.height - 3):
      input = grid.getInput(x + 1, y + 1, RADIUS)
      if input is False:
        continue
      output = net.activate(input)
      if output[0] >= 0.5:
        grid.placeBeacon(x, y)
  
  if grid.getFitness() >= 0:
    print("Best test fitness: "+str(float(grid.getFitness())/NUM_PUMPJACKS)+" beacons/pumpjack")
  else:
    print("Best test fitness: A pipe could not find a path out of the beacons, negative score.")
  grid.getBlueprint()



def run(config_file):

  config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_file)
    
  p = neat.Population(config)

  winner = p.run(eval_genomes, NUM_GENERATIONS)

  print('\nBest genome:\n{!s}'.format(winner))

config_path = os.path.join(os.path.dirname(__file__), 'config')
run(config_path)
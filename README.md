
# Factorio Pumpjack Beacon Evolver

So you want to make a bot that places beacons optimally, eh? Well, you've come to the right place.

## Installing

You need python (you gotta Google this one if you don't have it).

You'll need to install `astar` and `neat-python`:

```
pip install astar && pip install neat-python
```

This isn't strictly necessary, but if you want a blueprint to be outputted every 10 generations, you'll need to install factorio-blueprint in this folder. You can do that with the following command (on unix systems):

```
git clone https://github.com/demipixel/factorio-blueprint.git && cd factorio-blueprint && npm install && cd ..
```

You will need git, npm, and node installed.

**If you don't do this step, comment out os.system() command in grid.py**

## Options

At the top of index.py, we have a few options.

- RADIUS: The radius the algorithm can see from a location to determine if a beacon should be placed at the center. The diameter (length) of this square is `(2*RADIUS + 1)^2`. **If you change this**, you'll need to change `num_inputs` in the config to be `diameter*2 - 18`, which is `((2*RADIUS + 1)^2)*2 - 18`
- NUM_GRIDS: This many grids are generated and each individual in the population is tested on the same set of grids. Because we are trying to maximize the worst scores, the higher this number is, the more grids will be tested and therefore everyone in the population is much more likely to get a lower score. With a lower number, however, fitness of a given genome may become innacurate. Be aware, the simulation takes longer to run the higher you raise this.
- NUM_GENERATIONS: The number of generations to run before stopping
- NUM_PUMPJACKS: The number of pumpjacks to be placed on the grid
- SIZE_OF_GRID: The width and height of the grid that genomes are tested on

### Worst Count

This is a horrible name, but this is the number of "worst fitnesses" we keep track of. For example, if this is 5, then the 5 worst scoring grids for a genome are averaged together and made to be this genome's fitness. The reason we do this is so we don't optimize for a good average, but for a genome to almost always perform well.

```
START_WORST_COUNT = 5
END_WORST_COUNT = 3
WORST_COUNT_STEP_GENERATIONS = 50
WORST_COUNT_STEP_SIZE = -1
```

This means we start at a worse_count of 5, and every 50 generations we will decrease it until we stop at 3. Feel free to play around with these. If you set `NUM_GRIDS = START_WORST_COUNT = END_WORST_COUNT`, you'll always just take the average as the fitness.

### Play with the config

The config is specific to neat-python. Other than `num_inputs` and `num_outputs`, you can pretty much play with anything however you like. Change population, probability for mutations, crossover, etc. This can really have an imapct on how the population improves!
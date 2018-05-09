import random
import os
from astar import AStar

PUMPJACK_EXIT_DIRECTION = [
  (2, -1),
  (3, 0),
  (0, 3),
  (-1, 2)
]

SIDES = [
  (1, 0),
  (-1, 0),
  (0, 1),
  (0, -1)
]

class Grid():
  def __init__(self, width=32, height=32, randoms=10):
    self.width = width
    self.height = height
    self.grid = []

    for x in range(0, self.width):
      self.grid.append([])
      for y in range(0, self.height):
        self.grid[x].append(0)
      

    self.reset()
    self.pumpjack_dict = dict()
    self.pipe_starts = []

    for i in range(0, randoms):
      self.createRandomPumpjack()

  def get(self, x, y): # -1: off grid, 0: empty, 1: pumpjack, 2: pipe, 3: beacon
    return self.grid[x][y] if x >= 0 and y >= 0 and x < self.width and y < self.height else -1
  

  def reset(self):
    self.beacons = []

    for x in range(0, self.width):
      for y in range(0, self.height):
        if self.grid[x][y] == 3:
          self.grid[x][y] = 0
      
    
  

  def getBlueprint(self):
    node_cmd = "echo \""
    node_cmd += "const Blueprint = require('./factorio-blueprint');"
    node_cmd += "bp = new Blueprint();"
    for pos in self.pumpjack_dict.keys():
      rotation = 0
      for s in range(0, 4):
        if self.get(pos[0] + PUMPJACK_EXIT_DIRECTION[s][0], pos[1] + PUMPJACK_EXIT_DIRECTION[s][1]) == 2:
          rotation = s * 2
      
      node_cmd += "bp.createEntity('pumpjack', {x: "+str(pos[0])+", y: "+str(pos[1])+"},"+str(rotation)+");"

    for beacon_pos in self.beacons:
      node_cmd += "bp.createEntity('beacon', {x:"+str(beacon_pos[0])+", y:"+str(beacon_pos[1])+"});"

    for pipe_start in self.pipe_starts:
      node_cmd += "bp.createEntity('pipe', {x: "+str(pipe_start[0])+", y: "+str(pipe_start[1])+"});"

    node_cmd += "bp.fixCenter();"

    node_cmd += "console.log(bp.encode());"
    node_cmd += "\" | node"

    os.system(node_cmd)
  

  def createRandomPumpjack(self):
    placed = False
    while not placed:
      posX = random.randint(4, self.width - 3 - 4)
      posY = random.randint(4, self.height - 3 - 4)

      # Check to see if something is already in self location
      overlapping = False
      for x in range(posX - 2, posX + 3):
        if overlapping:
          break
        for y in range(posY - 2, posY + 3):
          if (self.get(x, y) != 0):
            overlapping = True
            break
          
        
      

      if overlapping:
        continue

      randomRotation = random.randint(0, 4)
      for i in range(0, 4):
        rot = (randomRotation + i) % 4
        pipeX = posX + PUMPJACK_EXIT_DIRECTION[rot][0]
        pipeY = posY + PUMPJACK_EXIT_DIRECTION[rot][1]
        if self.get(pipeX, pipeY) == 0 or self.get(pipeX, pipeY) == 2: # Free, on grid
          placed = True
          self.grid[pipeX][pipeY] = 2
          self.pipe_starts.append((pipeX, pipeY))
          self.pumpjack_dict[(posX, posY)] = (posX, posY)
          for x in range(posX, posX + 3):
            for y in range(posY, posY + 3):
              self.grid[x][y] = 1
            
          
          break
  

  def placeBeacon(self, posX, posY):
    for x in range(posX, posX + 3):
      for y in range(posY, posY + 3):
        if self.grid[x][y] != 0:
          return
      
    

    self.beacons.append((posX, posY))
    for x in range(posX, posX + 3):
      for y in range(posY, posY + 3):
        self.grid[x][y] = 3
      
    
  

  def getInput(self, posX, posY, radius=9):
    reach = False
    inputs = []
    for x in range(posX - radius, posX + radius + 1):
      for y in range(posY - radius, posY + radius + 1):
        if self.get(x, y) == 1 and x >= posX - 4 and x <= posX + 4 and y >= posY - 4 and y <= posY + 4:
          reach = True
        tile = self.get(x, y)
        if x < posX - 1 or x > posX + 1 or y < posY - 1 or y > posY + 1:
          inputs.append((1 if tile == 1 else 0.5) if (tile == 1 or tile == 2) else 0)
          inputs.append(1 if tile == 3 else 0)
      
    

    if not reach:
      return False

    return inputs
  

  def getFitness(self):
    total = 0
    for beacon_pos in self.beacons:
      for pumpjack_pos in self.pumpjack_dict:
        if abs(beacon_pos[0] - pumpjack_pos[0]) <= 5 and abs(beacon_pos[1] - pumpjack_pos[1]) <= 5:
          total += 1

    return total if self.canPipe() else -5 + float(total)/100*5
  

  def canPipe(self):
    for pipe_start in self.pipe_starts:
      
      path = PipeFinding(self).astar(pipe_start, (-1, -1))
      if path is None:
        return False
    
    return True
  
class PipeFinding(AStar):

  def __init__(self, grid):
    self.grid = grid
  
  def is_goal_reached(self, cur, goal):
    return cur[0] == goal[0] and cur[1] == goal[1]
  
  def neighbors(self, node):
    valid = []
    for side in SIDES:
      side_pos = (node[0] + side[0], node[1] + side[1])
      if self.grid.get(side_pos[0], side_pos[1]) <= 0 and side_pos[0] >= -1 and side_pos[1] >= -1 and side_pos[0] <= self.grid.width and side_pos[1] <= self.grid.height:
        valid.append(side_pos)
    
    return valid
  
  def distance_between(self, n1, n2):
    return abs(n1[0] - n2[0]) + abs(n1[1] - n2[1])
  
  def heuristic_cost_estimate(self, cur, goal):
    return self.distance_between(cur, goal)

# COMP90054 AI Planning for Autonomy Assignment 3
# Author: Emily Zhou 1081894

# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util, math
import game
from game import Directions

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'Collector', second = 'Collector'):

  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

# Parameter for calculating Q value and UCB
DISCOUNT = 0.95
EXPLORATION_CONSTANT = 0.3
LEARNING_RATE = 0.2

# Time limit to restrict calculation time per step
TIME_LIMIT = 0.8

# The agent who prefers collecting food on the enemy's side
class Collector(CaptureAgent):

  def registerInitialState(self, gameState):

    CaptureAgent.registerInitialState(self, gameState)

    # Initialization
    self.homeFood = []
    self.carrying = 0
    self.current_target = None
    self.boundary = self.getBoundary(gameState)
    self.prevAction = None
    self.prevPos = None
    self.startTime = 0
    self.safe = True
    
    self.rewards = getRewards(self)
    self.MCT = createMCT(gameState, self, None)

    # Maximum number of food carried to return
    self.maxCapacity = int(len(self.getFood(gameState).asList()) // 4)

  def chooseAction(self, gameState):
    
    # record time to be awared of time limit
    self.startTime = time.time()

    # find all possible actions to expand search tree
    nextActions = gameState.getLegalActions(self.index)

    # observe environment for choosing action
    pacmanEnemy = getPacmanEnemy(self, gameState)
    invincibleEnemy = getInvincibleEnemy(self, gameState)
    my_local_state = gameState.getAgentState(self.index)
    my_pos = my_local_state.getPosition()
    x = int(my_pos[0])
    y = int(my_pos[1])

    # re-spawn detection and reset
    if self.prevPos != None and util.manhattanDistance((x,y), self.prevPos) > 1:
      self.safe = True
      self.prevAction = None
      self.carrying = 0
      self.prevPos = None

    if self.prevAction != None and not oppositeAction(self.prevAction) in nextActions:
      self.safe = True
      self.prevAction = None
      self.carrying = 0
      self.prevPos = None


    # at the beginning of the game
    # the agent will safely approach the boundary through the fastest route
    if self.safe:
      self.current_target = self.getClosestPos(gameState,self.boundary)

      # switch to MCTS for uncertainty handling when cross / on the boundary
      if gameState.getAgentState(self.index).isPacman or (x,y) in self.boundary:
        self.safe = False
        return self.chooseAction(gameState)

      # switch to MCTS for uncertainty handling when enemy is detected
      if pacmanEnemy != [] or invincibleEnemy != []:
        for enemyPos in pacmanEnemy + invincibleEnemy:
          if util.manhattanDistance((x,y), enemyPos) <= 5:
            self.safe = False
            return self.chooseAction(gameState)

      

      problem = PositionSearchProblem(gameState,self.current_target,self.index)
      path  = self.aStarSearch(problem)
      
      ##################################################################
      # similar implementation of path extraction from baselineTeam.py #
      ##################################################################
      if path == []:
        self.prevAction = random.choice(nextActions)
        self.prevPos = (x,y)
        return self.prevAction
      else:
        action = path[0]
        dx,dy = game.Actions.directionToVector(action)
        new_x,new_y = int(x+dx),int(y+dy)
        if (new_x,new_y) == self.current_target:
          self.current_target = None
        if CaptureAgent.getFood(self, gameState)[new_x][new_y]:
          self.carrying +=1
        elif (new_x,new_y) in self.boundary:
          self.carrying = 0
        self.prevAction = path[0]
        self.prevPos = (x,y)
        return self.prevAction

    # use Monte-Carlo Tree Search and update Q table to select next best action  
    else:
      # born with enemy nearby
      if self.prevAction == None:
        self.current_target = self.getClosestPos(gameState,self.boundary)
        problem = PositionSearchProblem(gameState,self.current_target,self.index)
        path  = self.aStarSearch(problem)
        
        ##################################################################
        # similar implementation of path extraction from baselineTeam.py #
        ##################################################################
        if path == []:
          self.prevAction = random.choice(nextActions)
          self.prevPos = (x,y)
          return self.prevAction
        else:
          action = path[0]
          dx,dy = game.Actions.directionToVector(action)
          new_x,new_y = int(x+dx),int(y+dy)
          if (new_x,new_y) == self.current_target:
            self.current_target = None
          if CaptureAgent.getFood(self, gameState)[new_x][new_y]:
            self.carrying +=1
          elif (new_x,new_y) in self.boundary:
            self.carrying = 0
          self.prevAction = path[0]
          self.prevPos = (x,y)
          return self.prevAction
        

      # go back to boundary if in a safe environment: no enemy found, in home territory and not at boundary
      if pacmanEnemy == [] and invincibleEnemy == [] and not gameState.getAgentState(self.index).isPacman and not (x,y) in self.boundary:
        self.safe = True
        return self.chooseAction(gameState)

      # Game information
      height =gameState.data.layout.height
      width = gameState.data.layout.width
      
      self.rewards = getRewards(self)
      # stop collecting food when enough food is collected, prioritize returning to home side
      # [food, power capsule, pacman enemy, invincible enemy, boundary]
      if len(self.getFood(gameState).asList()) <= 2:
        enemy_nearby = False
        for enemyPos in pacmanEnemy + invincibleEnemy:
          if util.manhattanDistance((x,y), enemyPos) <= 5:
            enemy_nearby = True
            break
        if not enemy_nearby:
          self.current_target = self.getClosestPos(gameState,self.boundary)
          problem = PositionSearchProblem(gameState,self.current_target,self.index)
          path  = self.aStarSearch(problem)
          
          ##################################################################
          # similar implementation of path extraction from baselineTeam.py #
          ##################################################################
          if path == []:
            self.prevAction = random.choice(nextActions)
            self.prevPos = (x,y)
            return self.prevAction
          else:
            action = path[0]
            dx,dy = game.Actions.directionToVector(action)
            new_x,new_y = int(x+dx),int(y+dy)
            if (new_x,new_y) == self.current_target:
              self.current_target = None
            if CaptureAgent.getFood(self, gameState)[new_x][new_y]:
              self.carrying +=1
            elif (new_x,new_y) in self.boundary:
              self.carrying = 0
            self.prevAction = path[0]
            self.prevPos = (x,y)
            return self.prevAction
        else:
          self.rewards[0] = 0
          self.rewards[1] = 0
          self.rewards[4] = 300
      elif self.carrying >= self.maxCapacity:
        self.rewards[4] = 300

      self.MCT = createMCT(gameState, self, createChildNode(x, y, self.prevAction, None, -1))
      for i in range((height + width) * 3):
        if (time.time() - self.startTime > 0.8):
          break
        self.MCT = select(self.MCT, self, gameState, self.rewards, pacmanEnemy, invincibleEnemy, DISCOUNT, EXPLORATION_CONSTANT, LEARNING_RATE)
      
      qVal = []
      for nextNode in self.MCT[4]:
        qVal.append(nextNode[6])
      

      # entering empty dead end detection and turn around
      if isEnterDeadend(x, y, self.prevAction, gameState, self):
        nextActions = getAllNextActions(gameState, x, y)
        if oppositeAction(self.prevAction) in nextActions:
          self.prevAction = oppositeAction(self.prevAction)
        else:
          maxActions = getMaxAction(qVal)
          maxAction = random.choice(maxActions)
          self.prevAction = self.MCT[4][maxAction][2]

      # randomly select a best action found
      else:
        maxActions = getMaxAction(qVal)
        maxAction = random.choice(maxActions)
        self.prevAction = self.MCT[4][maxAction][2]
       
      # record food carried by an agent
        dx,dy = game.Actions.directionToVector(self.prevAction)
        new_x,new_y = int(x+dx),int(y+dy)
        if CaptureAgent.getFood(self, gameState)[new_x][new_y]:
          self.carrying +=1
        elif (new_x,new_y) in self.boundary:
          self.carrying = 0

      self.prevPos = (x,y)
      return self.prevAction

  ########################################
  # utilise methods from baselineTeam.py #
  ######################################## 
  def getClosestPos(self,gameState,pos_list):
    min_length = 9999
    min_pos = None
    my_local_state = gameState.getAgentState(self.index)
    my_pos = my_local_state.getPosition()
    for pos in pos_list:
      temp_length = self.getMazeDistance(my_pos,pos)
      if temp_length < min_length:
        min_length = temp_length
        min_pos = pos
    return min_pos
  
  def getBoundary(self,gameState):
    boundary_location = []
    height = gameState.data.layout.height
    width = gameState.data.layout.width
    for i in range(height):
      if self.red:
        j = int(width/2)-1
      else:
        j = int(width/2)
      if not gameState.hasWall(j,i):
        boundary_location.append((j,i))
    return boundary_location
        
  def aStarSearch(self, problem):
    """Search the node that has the lowest combined cost and heuristic first."""
    
    from util import PriorityQueue
    myPQ = util.PriorityQueue()
    startState = problem.getStartState()
    # print(f"start states {startState}")
    startNode = (startState, '',0, [])
    heuristic = problem._manhattanDistance
    myPQ.push(startNode,heuristic(startState))
    visited = set()
    best_g = dict()
    while not myPQ.isEmpty():
        node = myPQ.pop()
        state, action, cost, path = node
        # print(cost)
        # print(f"visited list is {visited}")
        # print(f"best_g list is {best_g}")
        if (not state in visited) or cost < best_g.get(str(state)):
            visited.add(state)
            best_g[str(state)]=cost
            if problem.isGoalState(state):
                path = path + [(state, action)]
                actions = [action[1] for action in path]
                del actions[0]
                return actions
            for succ in problem.getSuccessors(state):
                succState, succAction, succCost = succ
                newNode = (succState, succAction, cost + succCost, path + [(node, action)])
                myPQ.push(newNode,heuristic(succState)+cost+succCost)
    return []

######################################################
# utilise PositionSearchProblem from baselineTeam.py #
######################################################
class PositionSearchProblem:
    """
    It is the ancestor class for all the search problem class.
    A search problem defines the state space, start state, goal test, successor
    function and cost function.  This search problem can be used to find paths
    to a particular point.
    """

    def __init__(self, gameState, goal, agentIndex = 0,costFn = lambda x: 1):
        self.walls = gameState.getWalls()
        self.costFn = costFn
        x,y = gameState.getAgentState(agentIndex).getPosition()
        self.startState = int(x),int(y)
        self.goal_pos = goal

    def getStartState(self):
      return self.startState

    def isGoalState(self, state):

      return state == self.goal_pos

    def getSuccessors(self, state):
        successors = []
        for action in [game.Directions.NORTH, game.Directions.SOUTH, game.Directions.EAST, game.Directions.WEST]:
            x,y = state
            dx, dy = game.Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append( ( nextState, action, cost) )
        return successors

    def getCostOfActions(self, actions):
        if actions == None: return 999999
        x,y= self.getStartState()
        cost = 0
        for action in actions:
            # Check figure out the next state and see whether its' legal
            dx, dy = game.Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
            cost += self.costFn((x,y))
        return cost
      
    def _manhattanDistance(self,pos):
      return util.manhattanDistance(pos,self.goal_pos)

# initiate root node of MCT: [x, y, action, parent node, [next nodes], N, Q, layer]
def createMCT(gameState, self, parent): 
  my_local_state = gameState.getAgentState(self.index)
  my_pos = my_local_state.getPosition()
  x = int(my_pos[0])
  y = int(my_pos[1])
  rootnode = [x, y, self.prevAction, parent, [], 0, 0, 0]
  return rootnode

# create child node of MCT: [x, y, action, parent node, [next nodes], N, Q, layer]
def createChildNode(x, y, action, parentNode, layer):
  return [x, y, action, parentNode, [], 0, 0, layer]

# expand the MCT with all possible next states excluding turn back actions
def expand(node, gameState):
  # only expand unexpanded nodes
  if len(node[4]) == 0:
    # get all valid actions to calculate possible states
    nextActions = getAllNextActions(gameState, node[0], node[1])
    for nextAction in nextActions:
      if len(nextActions) > 1 and nextAction == oppositeAction(node[2]):
        continue
      else:
        next_x, next_y = getNextPos((node[0], node[1]), nextAction)
        childNode = createChildNode(next_x, next_y, nextAction, node, node[7]+1)
        node[4].append(childNode)

  return node

# the selection funcyion is applied recursively until a leaf node of MCT is reached
# reward is then calculated and result back propagated in the tree
def select(node, self, gameState, rewards, pacmanEnemy, invincibleEnemy, discount, explorationC, learningRate):
  # increase visited times of a node
  node[5] = node[5] + 1
  # tree expanded to find new leaf node
  node = expand(node, gameState)
  
  # expanded node waiting to be backpropagated
  if node[5] > 1:
    UCB = []
    for nextNode in node[4]:
      ucb = nextNode[6] + 2 * explorationC * math.sqrt((2 * math.log(node[5])) / max(nextNode[5], 1))
      UCB.append(ucb)
    maxActions = getMaxAction(UCB)
    selectedNextNode = random.choice(maxActions)
    nextNode = node[4][selectedNextNode]
    updatedNextNode = select(nextNode, self, gameState, rewards, pacmanEnemy, invincibleEnemy, discount, explorationC, LEARNING_RATE)
    node[6] = node[6] + (1/node[5]) * learningRate * (discount * updatedNextNode[6] - node[6])
    node[4][selectedNextNode] = updatedNextNode
    return node
  
  # new leaf node found, start simulation
  else:
    reward = simulate(node, node[7], self, gameState, rewards, pacmanEnemy, invincibleEnemy, discount)
    node[6] = node[6] + (1/node[5]) * learningRate * (discount * reward - node[6])
    return node

# One simulated game is played from selected node
def simulate(node, startLayer, self, gameState, rewards, pacmanEnemy, invincibleEnemy, discount):
  # Game information
  height = gameState.data.layout.height
  width = gameState.data.layout.width
  x = int(node[0])
  y = int(node[1])

  # goal detection
  # return to boundary when task is complete
  if len(self.getFood(gameState).asList()) <= 2 and (x, y) in self.boundary:
    return (rewards[4] * (discount ** (node[7]-startLayer-1)))
  elif self.carrying > 0 and (x, y) in self.boundary:
    return (rewards[4] * (self.carrying / self.maxCapacity) * (discount ** (node[7]-startLayer-1))) 
  # position of a food
  elif CaptureAgent.getFood(self, gameState)[x][y]:
    return (rewards[0] * (discount ** (node[7]-startLayer-1)))
  # position of a power capsule
  elif (x, y) in CaptureAgent.getCapsules(self, gameState):
    return (rewards[1] * (discount ** (node[7]-startLayer-1)))
  # position of a pacman enemy
  elif (x, y) in pacmanEnemy:
    return (rewards[2] * (discount ** (node[7]-startLayer-1)))
  # position of an invincible enemy
  elif (x, y) in invincibleEnemy:
    return (rewards[3] * (discount ** (node[7]-startLayer-1)))
  # position of an empty dead end, make simulation invalid to save time
  elif isEnterDeadend(x, y, node[2], gameState, self):
    return 0
  # stop simulating at a threshold distance
  elif (node[7] > (height + width) / 2):
    return 0

  # randomly choose actions and continue simulation
  node = expand(node, gameState)
  selectedNextNode = random.choice(range(len(node[4])))
  nextNode = node[4][selectedNextNode]
  return simulate(nextNode, startLayer, self, gameState, rewards, pacmanEnemy, invincibleEnemy, discount)

# define rewards of different scenario for the collector agent
# even index agents are collectors who prefer colleting food, more aggressive
# odd index agents are collectors who prefer attack enemy when possible
# [food, power capsule, pacman enemy, invincible enemy, boundary]
def getRewards(self):
   if (self.index+1 // 2) == 1:
    return [120, 100, 80, -150, 0]
   else:
    return [80, 100, 120, -150, 0]
   
# get next position of a legal action in integer format
def getNextPos(pos, action):
   next = game.Actions.getSuccessor(pos, action)
   return ((int(next[0]), int(next[1])))

# get the coordinates of detected invaders when they are not invincible
def getPacmanEnemy(self, gameState):

  enemies = self.getOpponents(gameState)
  hasInvader = False

  # Invader detection
  for enemy in enemies:
      # in our territory and does not have power capsule
      if gameState.getAgentState(enemy).isPacman and gameState.getAgentState(self.index).scaredTimer == 0:
        hasInvader = True
        break
  
  enemyFound = []
  if not hasInvader:
    return enemyFound
  
  else:
    # invader detected within range
    for enemy in enemies:
      enemyState = gameState.getAgentState(enemy)
      enemyPos = enemyState.getPosition()
      if enemyState.isPacman and enemyPos != None:
        x, y = enemyPos
        enemyPos = (int(x), int(y))
        enemyFound.append(enemyPos)

  return enemyFound
    
# get the coordinates of defending enemy in their territory
# or invaders when they are invincible (had power capsule)
def getInvincibleEnemy(self, gameState):

  enemies = self.getOpponents(gameState)
  hasDefender = False

  # defensive enemy detection
  for enemy in enemies:
      if not gameState.getAgentState(enemy).isPacman or gameState.getAgentState(self.index).scaredTimer > 0:
        hasDefender = True
        break
  
  enemyFound = []
  if not hasDefender:
    return enemyFound
  
  else:
    # defensive enemy detected within range
    for enemy in enemies:
      enemyState = gameState.getAgentState(enemy)
      enemyPos = enemyState.getPosition()
      # is a defender or has power capsule
      if (not enemyState.isPacman or gameState.getAgentState(self.index).scaredTimer > 0) and enemyPos != None:
        x, y = enemyPos
        enemyPos = (int(x), int(y))
        enemyFound.append(enemyPos)
      
      # is a Pacman enemy likely to become invincible by returning home
      if (enemyState.isPacman and enemyPos in self.boundary) and enemyPos != None:
        x, y = enemyPos
        enemyPos = (int(x), int(y))
        enemyFound.append(enemyPos)

  return enemyFound

# find indeces of best actions with highest Q value according to the provided Q table
def getMaxAction(valList):
  maxVal = max(valList)
  maxVals = []
  for i in range(len(valList)):
    if valList[i] == maxVal:
      maxVals.append(i)
  return maxVals

# return opposite direction
def oppositeAction(action):
  if action == Directions.EAST:
    return Directions.WEST
  elif action == Directions.WEST:
    return Directions.EAST
  elif action == Directions.NORTH:
    return Directions.SOUTH
  elif action == Directions.SOUTH:
    return Directions.NORTH

# get all valid actions from a coordinate
def getAllNextActions(gameState, x, y):
  height =gameState.data.layout.height
  width = gameState.data.layout.width
  nextActions = []
  for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
    dx, dy = game.Actions.directionToVector(action)
    nextx, nexty = int(x + dx), int(y + dy)
    if not gameState.getWalls()[nextx][nexty]:
      nextActions.append(action)
  return nextActions

# detect whether the given position is an empty dead end
def isDeadend(x, y, gameState, self):
  nextActions = getAllNextActions(gameState, x, y)
  if len(nextActions) == 1:
    if (not CaptureAgent.getFood(self, gameState)[int(x)][int(y)]) and (not (int(x), int(y)) in CaptureAgent.getCapsules(self, gameState)):
      return True
  return False

# detect whether the planned route ahead is an empty dead end, explore recursively
def isEnterDeadend(x, y, action, gameState, self):
  
  nextActions = getAllNextActions(gameState, x, y)
  
  # reach dead end
  if len(nextActions) == 1:
    if isDeadend(x, y, gameState, self):
      return True
    else:
      return False
    
  # reach a junction, not a dead end
  elif len(nextActions) > 2:
    return False

  elif len(nextActions) == 2:
    # at a turn and continue to explore if there is dead end ahead
    if not action in nextActions:
      nextActions.remove(oppositeAction(action))
      nextAction = nextActions[0]
      x, y = getNextPos((x, y), nextAction)
      return isEnterDeadend(x, y, nextAction, gameState, self)
    # continue exploring straight ahead
    else:
      x, y = getNextPos((x, y), action)
      return isEnterDeadend(x, y, action, gameState, self)
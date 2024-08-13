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
import random, time, util
import game
from game import Directions


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='Offender', second='Defender'):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
##########

MAX_CAPACITY = 5


class Offender(CaptureAgent):
    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''
        CaptureAgent.registerInitialState(self, gameState)

        '''
        Your initialization code goes here, if you need any.
        '''
        self.carrying = 0
        self.current_target = None
        self.boundary = self.getBoundary(gameState)
        self.eaten_half = False
        self.direction = Directions.STOP

    #This function is used to predict actions and positions of the opponents.
    #The positions of the opponents is transfered to the coordinates.
    def predictOpponentPositions(self, gameState, opponentActions, competitorsIndex):
        predictedPositions = []
        competitorsPos = self.getComPos(gameState, competitorsIndex)
        for comIndex, action in enumerate(opponentActions):
            if action:
                comState = gameState.getAgentState(comIndex)
                if not comState.isPacman:
                    continue

                comPosition = comState.getPosition()
                if comPosition is not None and not gameState.getAgentState(comIndex).isPacman:
                    x, y = comPosition
                    comPosition = (int(x), int(y))
                    competitorsPos.append(comPosition)
                    dx, dy = game.Actions.directionToVector(action)
                    nextX, nextY = int(x + dx), int(y + dy)
                    predictedPositions.append((nextX, nextY))
        return predictedPositions

    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        #Initializing states
        competitorsIndex = self.getOpponents(gameState)
        myPosition = gameState.getAgentPosition(self.index)
        capList = self.getCapsules(gameState)
        foods = self.getFood(gameState)

        #Opponents actions are stored in a list and the following detected actions will be stored in this list for future use.
        opponentActions = []
        for opponent in competitorsIndex:
            opponentState = gameState.getAgentState(opponent)
            if opponentState is not None:
                opponentAction = self.direction
                if opponentAction is not None:
                    opponentActions.append(opponentAction)

        # Predict competitor/oppenent position based on their actions
        predictedOpponentPositions = self.predictOpponentPositions(gameState, opponentActions, competitorsIndex)

        # Adjust the chosen action based on the position of competitor/opponent
        if predictedOpponentPositions:
            # Find the nearest competitor/oppenent's position
            nearestOpponent = min(predictedOpponentPositions, key=lambda x: self.getMazeDistance(myPosition, x))
            competitorsPos = self.getComPos(gameState, competitorsIndex)
            # Choose the action based on the position of competitor/opponent
            self.current_target = nearestOpponent
            problem = PositionSearchProblem(gameState, self.current_target, self.index,
                                            self.getDangerousPos(competitorsPos, gameState))
            path = self.aStarSearch(problem)
            if path == []:
                actions = gameState.getLegalActions(self.index)
                return random.choice(actions)
            else:
                action = path[0]
                dx, dy = game.Actions.directionToVector(action)
                x, y = gameState.getAgentState(self.index).getPosition()
                new_x, new_y = int(x + dx), int(y + dy)
                if (new_x, new_y) == self.current_target:
                    self.current_target = None
                if self.getFood(gameState)[new_x][new_y]:
                    self.carrying += 1
                elif (new_x, new_y) in self.boundary:
                    self.carrying = 0
                return path[0]

        #Finding the safe target on the team side.
        #Prevent the offender when it goes into competitor boundary and meets competitor ghost,
        #and this is implemented as choose another path to get into competitor half.
        def safeTarget(self, gameState, competitorsIndex):
            if myPosition in self.boundary:
                for comIndex in competitorsIndex:
                    competitorState = gameState.getAgentState(comIndex)
                    comPosition = competitorState.getPosition()
                    if comPosition and not gameState.getAgentState(comIndex).isPacman:
                        x, y = comPosition
                        comPosition = (int(x), int(y))
                        if self.getMazeDistance(myPosition, comPosition) <= 2:
                            safePath = []
                            for pos in self.boundary:
                                if pos not in self.getCompetitorBoundary(gameState):
                                    safePath.append(pos)
                            if safePath:
                                self.current_target = random.choice(safePath)
                            else:
                                pass
                            break

        # When the offender is in ghost mode:
        if not gameState.getAgentState(self.index).isPacman:
            ifChange = False
            safeTarget(self, gameState, competitorsIndex)
            if not ifChange:
                if not self.current_target == None:
                    pass
                else:
                    self.current_target = self.getClosestPos(gameState, foods.asList())
            problem = PositionSearchProblem(gameState, self.current_target, self.index)

        #When the offender is in Pacman mode
        #If the offender can still eat before competitor ghose scared time is up, it will continue to eat food
        else:
            continueEat = gameState.getAgentState(competitorsIndex[0]).scaredTimer
            competitorsPos = []
            if continueEat > 2:
                if self.current_target == None or self.current_target not in foods.asList():
                    self.current_target = self.getClosestPos(gameState, foods.asList())
                else:
                    pass
        #If the time is less than 2, the target will chosen depending on the conditions.
        #Condition: return team boundary if the pacman eat the most food as it can. Or the food for pacman is less than 2.
        #Condition: Pacman will go eat the capsule if there's any.
        #Condition: If there's no capsule or food is enough for pacman to eat or not at max capacity, eat food.
        #Eating strategy is designed as eat the half(top or bottom) part in the competitor side depending on the comparison of remaining food in both part.
            else:
                comHalfTop = [(x, y) for x in range(gameState.data.layout.width) for y in range(gameState.data.layout.height // 2)]
                comHalfBottom = [(x, y) for x in range(gameState.data.layout.width) for y in
                                        range(gameState.data.layout.height // 2, gameState.data.layout.height)]

                remainTop = len([pos for pos in self.getFood(gameState).asList() if pos in comHalfTop])
                remainBottom = len([pos for pos in self.getFood(gameState).asList() if pos in comHalfBottom])

                competitorsPos = self.getComPos(gameState, competitorsIndex)
                if not self.current_target == None:
                    pass
                else:
                    if (len(capList) > 0):
                        self.current_target = self.getClosestPos(gameState, capList)
                    else:
                        self.current_target = self.getClosestPos(gameState, foods.asList())
                if self.carrying < MAX_CAPACITY:
                    if remainTop > remainBottom:
                        self.current_target = self.getClosestPos(gameState,
                                                             [pos for pos in self.getFood(gameState).asList() if
                                                              pos in comHalfTop])
                    elif remainBottom > remainTop:
                        self.current_target = self.getClosestPos(gameState,
                                                             [pos for pos in self.getFood(gameState).asList() if
                                                              pos in comHalfBottom])
                elif len(self.getFood(gameState).asList()) <= 2:
                    self.current_target = self.getClosestPos(gameState, self.boundary)
                else:
                    self.current_target = self.getClosestPos(gameState, self.boundary)

            problem = PositionSearchProblem(gameState, self.current_target, self.index, self.getDangerousPos(competitorsPos, gameState))

        path = self.aStarSearch(problem)
        if path == []:
            actions = gameState.getLegalActions(self.index)
            return random.choice(actions)
        else:
            action = path[0]
            dx, dy = game.Actions.directionToVector(action)
            x, y = gameState.getAgentState(self.index).getPosition()
            new_x, new_y = int(x + dx), int(y + dy)
            if (new_x, new_y) == self.current_target:
                self.current_target = None
            if self.getFood(gameState)[new_x][new_y]:
                self.carrying += 1
            elif (new_x, new_y) in self.boundary:
                self.carrying = 0
            return path[0]

    #This function is to know dangerous position to prevent the defender or offender to reach the position.
    def getDangerousPos(self, competitorsPos, gameState):
        height = gameState.data.layout.height
        width = gameState.data.layout.width
        res = []
        for i in range(height):
            for j in range(width):
                for comPosition in competitorsPos:
                    if not gameState.hasWall(j,i) and self.getMazeDistance((j,i),comPosition) <= 3:
                        res.append((j,i))
        return res

    def getClosestPos(self, gameState, pos_list):
        min_length = 9999
        min_pos = None
        my_local_state = gameState.getAgentState(self.index)
        my_pos = my_local_state.getPosition()
        for pos in pos_list:
            temp_length = self.getMazeDistance(my_pos, pos)
            if temp_length < min_length:
                min_length = temp_length
                min_pos = pos
        return min_pos

    #This function is to get the  position of competitor in ghost mode.
    def getComPos(self, gameState, competitorsIndex):
        competitorsPos = []
        for compIndex in competitorsIndex:
            competitorState = gameState.getAgentState(compIndex)
            comPosition = competitorState.getPosition()
            if comPosition is not None and not gameState.getAgentState(compIndex).isPacman:
                x, y = comPosition
                comPosition = (int(x), int(y))
                competitorsPos.append(comPosition)
        return competitorsPos

    def getBoundary(self, gameState):
        boundary_location = []
        height = gameState.data.layout.height
        width = gameState.data.layout.width
        for i in range(height):
            if self.red:
                j = int(width / 2) - 1
            else:
                j = int(width / 2)
            if not gameState.hasWall(j, i):
                boundary_location.append((j, i))
        return boundary_location

    def aStarSearch(self, problem):
        """Search the node that has the lowest combined cost and heuristic first."""

        from util import PriorityQueue
        myPQ = util.PriorityQueue()
        startState = problem.getStartState()
        # print(f"start states {startState}")
        startNode = (startState, '', 0, [])
        heuristic = problem._manhattanDistance
        myPQ.push(startNode, heuristic(startState))
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
                best_g[str(state)] = cost
                if problem.isGoalState(state):
                    path = path + [(state, action)]
                    actions = [action[1] for action in path]
                    del actions[0]
                    return actions
                for succ in problem.getSuccessors(state):
                    succState, succAction, succCost = succ
                    newNode = (succState, succAction, cost + succCost, path + [(node, action)])
                    myPQ.push(newNode, heuristic(succState) + cost + succCost)
        return []

    #This function is to get the boundary of competitor side for offender in ghost mode
    def getCompetitorBoundary(self, gameState):
        comHalf = []
        width = gameState.data.layout.width
        height = gameState.data.layout.height
        if self.red:
            for i in range(width // 2, width):
                for j in range(height):
                    comHalf.append((i, j))
        else:
            for i in range(width // 2):
                for j in range(height):
                    comHalf.append((i, j))
        return comHalf


class Defender(Offender):
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)

        '''
        Your initialization code goes here, if you need any.
        '''
        self.carrying = 0
        self.current_target = None
        self.boundary = self.getBoundary(gameState)
        self.previousFoodList = []
        self.direction = Directions.STOP

    def predictOpponentPositions(self, gameState, opponentActions, competitorsIndex):
        predictedPositions = []
        competitorsPos = self.getComPos(gameState, competitorsIndex)
        for comIndex, action in enumerate(opponentActions):
            if action:
                comState = gameState.getAgentState(comIndex)
                if not comState.isPacman:
                    continue  # Only predict the opponent's position if it's not a ghost

                comPosition = comState.getPosition()
                if comPosition is not None and not gameState.getAgentState(comIndex).isPacman:
                    x, y = comPosition
                    comPosition = (int(x), int(y))
                    competitorsPos.append(comPosition)
                    dx, dy = game.Actions.directionToVector(action)
                    nextX, nextY = int(x + dx), int(y + dy)
                    predictedPositions.append((nextX, nextY))
        return predictedPositions

    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        # Initializing states
        competitorsIndex = self.getOpponents(gameState)
        currentFood = self.getFoodYouAreDefending(gameState).asList()
        comPacman = False
        for comIndex in competitorsIndex:
            if gameState.getAgentState(comIndex).isPacman:
                comPacman = True
        myPosition = gameState.getAgentPosition(self.index)

        # 获取对手动作
        opponentActions = []
        for opponent in competitorsIndex:
            opponentState = gameState.getAgentState(opponent)
            if opponentState is not None:
                opponentAction = self.direction
                if opponentAction is not None:
                    opponentActions.append(opponentAction)

        # 根据对手动作预测对手位置
        predictedOpponentPositions = self.predictOpponentPositions(gameState, opponentActions, competitorsIndex)

        # 根据对手位置调整选择的行动
        if predictedOpponentPositions:
            competitorsPos = self.getComPos(gameState, competitorsIndex)
            # 找到距离最近的对手位置
            nearestOpponent = min(predictedOpponentPositions, key=lambda x: self.getMazeDistance(myPosition, x))

            # 根据最近的对手位置选择行动
            self.current_target = nearestOpponent
            problem = PositionSearchProblem(gameState, self.current_target, self.index,
                                            self.getDangerousPos(competitorsPos, gameState))

            path = self.aStarSearch(problem)
            if path == []:
                actions = gameState.getLegalActions(self.index)
                return random.choice(actions)
            else:
                action = path[0]
                dx, dy = game.Actions.directionToVector(action)
                x, y = gameState.getAgentState(self.index).getPosition()
                new_x, new_y = int(x + dx), int(y + dy)
                if (new_x, new_y) == self.current_target:
                    self.current_target = None
                if self.getFood(gameState)[new_x][new_y]:
                    self.carrying += 1
                elif (new_x, new_y) in self.boundary:
                    self.carrying = 0
                return path[0]

        #getBoundaryDefender is called
        comBoundary = self.getBoundaryDefender(gameState)
        #If the pacman of competitor has not been found, find boudary to defense randomly.
        #However, once the pacman of competitor is found, the defender will chase the competitor pacman until that pacman is eaten.
        #The foodlist will also be stored as a guide to see whether there's foods have been eaten by competitor pacman.
        #Once the foodlist is not same as the previous stored foodlist, the defender will know competitor pacman has came to team side.
        if not comPacman:
            if not self.current_target == None:
                pass
            else:
                self.current_target = random.choice(self.boundary)
            problem = PositionSearchProblem(gameState, self.current_target, self.index, comBoundary)
        else:
            defensive = []
            for comIndex in competitorsIndex:
                competitorState = gameState.getAgentState(comIndex)
                comPosition = competitorState.getPosition()
                if competitorState.isPacman and comPosition != None:
                    x, y = comPosition
                    comPosition = (int(x), int(y))
                    defensive.append(comPosition)

            self.defensePosition(currentFood, defensive, self.previousFoodList)
            self.previousFoodList = currentFood

            if len(defensive) > 0:
                self.current_target = self.getClosestPos(gameState, defensive)
            else:
                if not self.current_target == None:
                    pass
                else:
                    self.current_target = self.getClosestPos(gameState, currentFood)
            if gameState.getAgentState(self.index).scaredTimer > 0:
                problem = PositionSearchProblem(gameState, self.current_target, self.index, comBoundary + self.getDangerousPos(defensive, gameState))
            else:
                problem = PositionSearchProblem(gameState, self.current_target, self.index, comBoundary)

        path = self.aStarSearch(problem)

        if path == []:
            actions = gameState.getLegalActions(self.index)
            return random.choice(actions)
        else:
            action = path[0]
            dx, dy = game.Actions.directionToVector(action)
            x, y = gameState.getAgentState(self.index).getPosition()
            new_x, new_y = int(x + dx), int(y + dy)
            if (new_x, new_y) == self.current_target:
                self.current_target = None
            if self.getFood(gameState)[new_x][new_y]:
                self.carrying += 1
            elif (new_x, new_y) in self.boundary:
                self.carrying = 0
            return path[0]

    def defensePosition(self, currentFood, defensive, previousFoodList):
        if len(currentFood) < len(previousFoodList):
            foodHad = set(previousFoodList) - set(currentFood)
            while len(foodHad) != 0:
                foodPos = foodHad.pop()
                if foodPos not in defensive:
                    defensive.append(foodPos)

    #This function is to get the boundary of the competitor for the defender
    def getBoundaryDefender(self, gameState):
        comBoundary = []
        height = gameState.data.layout.height
        width = gameState.data.layout.width

        for i in range(height):
            if self.red:
                j = int(width / 2)
            else:
                j = int(width / 2) - 1

            if not gameState.hasWall(j, i):
                comBoundary.append((j, i))

        return comBoundary


class PositionSearchProblem:
    """
    It is the ancestor class for all the search problem class.
    A search problem defines the state space, start state, goal test, successor
    function and cost function.  This search problem can be used to find paths
    to a particular point.
    """

    def __init__(self, gameState, goal, agentIndex=0, dangerous = [], costFn=lambda x: 1):
        self.walls = gameState.getWalls().copy()
        for (x, y) in dangerous:
            self.walls[x][y] = True
        self.costFn = costFn
        x, y = gameState.getAgentState(agentIndex).getPosition()
        self.startState = int(x), int(y)
        self.goal_pos = goal

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):

        return state == self.goal_pos

    def getSuccessors(self, state):
        successors = []
        for action in [game.Directions.NORTH, game.Directions.SOUTH, game.Directions.EAST, game.Directions.WEST]:
            x, y = state
            dx, dy = game.Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append((nextState, action, cost))
        return successors

    def getCostOfActions(self, actions):
        if actions == None: return 999999
        x, y = self.getStartState()
        cost = 0
        for action in actions:
            # Check figure out the next state and see whether its' legal
            dx, dy = game.Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
            cost += self.costFn((x, y))
        return cost

    def _manhattanDistance(self, pos):
        return util.manhattanDistance(pos, self.goal_pos)



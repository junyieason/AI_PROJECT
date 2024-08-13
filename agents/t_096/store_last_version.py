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
import json

from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='Attack_Agent', second='Semi_Attack_Defence_Agent'):
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

MAX_CAPACITY = 7
TIMELIMIT = 10


###########
# Q_learning Agent
############

def get_weight(file_name):
    weight_data = [1, 1, 1]
    with open(file_name, 'r', encoding='utf-8') as weight_file:
        weight_data = json.load(weight_file)['feature_weight']
    return weight_data


class q_attack_agent(CaptureAgent):

    ## get the number of enemy food at the begging of the game
    def get_num_food(self, gameState):
        food_list = self.getFood(gameState).asList()
        number_food = len(food_list)
        return number_food

    """
    check whether the  agent is a ghost or a pacman
    """

    def get_agent_mode(self, gameState, enemy_index):
        # true = pacman  false = ghost
        if enemy_index is not None:
            result = gameState.getAgentState(enemy_index).isPacman
        else:
            result = gameState.getAgentState(self.index).isPacman
        return result

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

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        ## get the initial number of enemy's food
        self.total_food_initial = self.get_num_food(gameState)
        ## get the feature weight and set the weight to the agent
        weight = get_weight("agents/t_096/weight.json")
        self.feature_weight = weight
        ## current carrying food
        self.last_remaining_food = 0
        self.boundary = self.getBoundary(gameState)
        self.carrying = 0

    def feature_calculator(self, action, gameState):
        feature_list = []
        current_food_condition = self.getFood(gameState).asList()
        current_location = gameState.getAgentPosition(self.index)
        #########
        food_list = self.getFood(gameState).asList()
        current_food_remaining = len(food_list)
        #########
        next_state = gameState.generateSuccessor(self.index, action)
        next_location = next_state.getAgentPosition(self.index)
        next_food_condition = self.getFood(next_state).asList()
        next_number_food = len(next_food_condition)
        if (current_food_remaining > 2):
            ### food carrying
            dx, dy = game.Actions.directionToVector(action)
            x, y = gameState.getAgentState(self.index).getPosition()
            new_x, new_y = int(x + dx), int(y + dy)
            cache_carry = self.carrying
            if self.getFood(gameState)[new_x][new_y]:
                cache_carry += 1
            print("self.total_food_initial")
            print(self.total_food_initial)
            print("cache. carry")
            print(cache_carry)
            feature_list.append(1 / ((self.total_food_initial + 2) - cache_carry))
        else:
            feature_list.append(1 / self.total_food_initial + 2)

        ### number of food gain 看：到下一个state food 能多拿几个
        gain_food = self.last_remaining_food - next_number_food

        feature_list.append(1 / (self.total_food_initial - gain_food + 1))

        ### disntance to food 对于现在这个state
        min_dis = 100000000
        for next_food in next_food_condition:
            next_distance = self.getMazeDistance(next_location, next_food)
            if next_distance < min_dis:
                min_dis = next_distance

        feature_list.append(1 / (min_dis + 1))

        return feature_list

    def q_calculator(self, action, gameState):
        feature = self.feature_calculator(action, gameState)
        #####
        # 检查weight feature 长度
        #####
        q = 0
        for f_index in range(len(feature)):
            q += self.feature_weight[f_index] * feature[f_index]
        return q

    def get_best_action(self, begin_time, gameState, legal_action, return_action):
        iter_Q = -1000000000
        result_action = return_action
        for action in legal_action:
            time_gap = time.time() - begin_time
            if time_gap > TIMELIMIT:
                print("run out of time")
                break
            current_q = self.q_calculator(action, gameState)
            print(current_q)
            if (current_q > iter_Q):
                iter_Q = current_q
                result_action = action
        return result_action

    def chooseAction(self, gameState):
        # get the initial information for decision
        self_index = self.index
        self_location = gameState.getAgentPosition(self_index)
        enemy_index = self.getOpponents(gameState)  # get the enemy index
        capsules = self.getCapsules(gameState)  # get the list of capsules
        food_list = self.getFood(gameState).asList()
        current_mode = self.get_agent_mode(gameState, None)
        current_food_remaining = len(food_list)
        if (current_food_remaining > 2):
            begin_time = time.time()
            agent_mode = self.get_agent_mode(gameState, None)
            if not agent_mode:
                self.last_remaining_food = self.get_num_food(gameState)
            legal_actions = gameState.getLegalActions(self.index)
            return_action = legal_actions[0]

            if len(legal_actions) > 1:
                return_action = self.get_best_action(begin_time, gameState, legal_actions, return_action)
            print(return_action)
            ####################

            dx, dy = game.Actions.directionToVector(return_action)
            x, y = gameState.getAgentState(self.index).getPosition()
            new_x, new_y = int(x + dx), int(y + dy)
            if self.getFood(gameState)[new_x][new_y]:
                self.carrying += 1
            elif (new_x, new_y) in self.boundary:
                self.carrying = 0

            ####################

            return return_action
        else:  # when the number of eaten food have reach the goal go back to home and avoid the defence
            self.current_target = self.getClosestPos(gameState, self.boundary)
            self.return_permission = True
            enemy_location_list = self.get_enemyloc_list(gameState, enemy_index)
            problem = PositionSearchProblem(gameState, self.current_target, self.index, enemy_location_list)

            # the path finding logic(line 266 to line 284) is same as the sample/baselineTeam line 110 to line 124
            # author: University of Melbourne COMP90054 staff team
            # find a path
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

    def get_enemyloc_list(self, gameState, enemy_index):
        enemy_location_list = []
        for enemy_id in enemy_index:
            enemy_location = gameState.getAgentState(enemy_id).getPosition()
            # pacman = true ghost = false
            enemy_mode = self.get_agent_mode(gameState, enemy_id)
            if not enemy_mode and enemy_location is not None:
                exact_enemy_loc = form_enemy_location(enemy_location)
                enemy_location_list.append(exact_enemy_loc)
        return enemy_location_list

        # The method getClosestPos is same as the method getClosestPos in sample/baselineTeam
        # author: University of Melbourne COMP90054 staff team

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

        # The method  aStarSearch is same as the method aStarSearch in sample/baselineTeam
        # author: University of Melbourne COMP90054 staff team

    def aStarSearch(self, problem):
        """Search the node that has the lowest combined cost and heuristic first."""

        from util import PriorityQueue
        myPQ = util.PriorityQueue()
        startState = problem.getStartState()

        startNode = (startState, '', 0, [])
        heuristic = problem._manhattanDistance
        myPQ.push(startNode, heuristic(startState))
        visited = set()
        best_g = dict()
        while not myPQ.isEmpty():
            node = myPQ.pop()
            state, action, cost, path = node

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


"""
generate the int tuple enemy location
"""


def form_enemy_location(enemy_location):
    x_loc, y_loc = enemy_location
    return int(x_loc), int(y_loc)


"""
check whether there is a enemy agent around(with in 5 step)
"""


def enemy_around(enemy_location):
    if enemy_location is None:
        return False
    else:
        return True


class Attack_Agent(CaptureAgent):
    """
    An aggressive agent that  attack the enemy's field and eating food.
    It can avoid the attack by the enemy ghost, and it can automatically
    attack enemy's scared ghost.
    """

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
        self.attack_permission = True
        self.return_permission = False

    """
    check whether the  agent is a ghost or a pacman
    """

    def get_agent_mode(self, gameState, enemy_index):
        # true = pacman  false = ghost
        if enemy_index is not None:
            result = gameState.getAgentState(enemy_index).isPacman
        else:
            result = gameState.getAgentState(self.index).isPacman
        return result

    """
    check whether the agent arrive the boundary or not
    """

    def at_boundary(self, location):
        result = location in self.boundary
        return result

    """
    check whether current agent have a target or not
    """

    def have_target(self):
        if self.current_target is None:
            return False
        else:
            return True

    """
    set the initial target for first round attack
    """

    def get_initial_food_target(self, gameState, food_list):
        food_location = self.getClosestPos(gameState, food_list)
        return food_location

    """
    The method is used to avoid the enemy defence agent in the enemy's filed
    The attack agent are able to choose a valid path so that when the it cross
    the middle boarder the agent can not be caught.
    """

    def cross_boundary(self, gameState, enemy_index, self_location):
        for enemy_id in enemy_index:
            enemy_location = gameState.getAgentState(enemy_id).getPosition()
            if enemy_around(enemy_location):
                exact_enemy_location = form_enemy_location(enemy_location)
                if not self.get_agent_mode(gameState, enemy_id) and self.getMazeDistance(self_location,
                                                                                         exact_enemy_location):
                    self.attack_permission = False
                    new_boundary = self.boundary.copy()
                    new_boundary.remove(self_location)
                    current_choice = random.choice(new_boundary)
                    self.current_target = current_choice
                    break

    """
    The method is able to get the global minimum scared ghost time
    """

    def get_minimum_pro_time(self, gameState, enemy_index):
        timer_first = gameState.getAgentState(enemy_index[0]).scaredTimer
        timer_second = gameState.getAgentState(enemy_index[1]).scaredTimer
        if timer_first >= timer_second:
            return timer_second
        else:
            return timer_first

    """
    Get all the enemy agent location, if enemy's location can be detect (with in 5 step) 
    """

    def get_enemyloc_list(self, gameState, enemy_index):
        enemy_location_list = []
        for enemy_id in enemy_index:
            enemy_location = gameState.getAgentState(enemy_id).getPosition()
            # pacman = true ghost = false
            enemy_mode = self.get_agent_mode(gameState, enemy_id)
            if not enemy_mode and enemy_location is not None:
                exact_enemy_loc = form_enemy_location(enemy_location)
                enemy_location_list.append(exact_enemy_loc)
        return enemy_location_list

    def chooseAction(self, gameState):
        # get the initial information for decision
        self_index = self.index
        self_location = gameState.getAgentPosition(self_index)
        enemy_index = self.getOpponents(gameState)  # get the enemy index
        capsules = self.getCapsules(gameState)  # get the list of capsules
        food_list = self.getFood(gameState).asList()
        current_mode = self.get_agent_mode(gameState, None)
        current_food_remaining = len(food_list)
        if (current_food_remaining > 2):
            # home mode
            if not current_mode:  # whe the agent did not cross the middle line
                self.attack_permission = True  # refresh the attack permission every round
                if self.at_boundary(self_location):
                    self.cross_boundary(gameState, enemy_index, self_location)
                if self.attack_permission:
                    if self.have_target():
                        pass
                    else:
                        self.current_target = self.get_initial_food_target(gameState, food_list)
                problem = PositionSearchProblem(gameState, self.current_target, self.index)

            # at opponent mode
            else:  # when the agent cross the middle line
                enemy_location_list = self.get_enemyloc_list(gameState, enemy_index)
                pro_time = self.get_minimum_pro_time(gameState, enemy_index)
                current_target = self.current_target
                current_target_is_food = current_target in food_list
                # when the pacman eat the capsule
                if pro_time >= 2:
                    current_food_remaining = len(food_list)
                    if not current_target_is_food or current_target is None:
                        # when there are food remaining

                        # if current_food_remaining > 2 and current_target is None:
                        #     self.current_target = self.getClosestPos(gameState, food_list)
                        # # when the pacman can not eat food-> start eat ghost
                        # elif len(enemy_location_list) > 0:
                        #     self.current_target = self.getClosestPos(gameState, enemy_location_list)

                        if len(enemy_location_list) > 0:
                            self.current_target = self.getClosestPos(gameState, enemy_location_list)
                        elif current_food_remaining > 2 and self.current_target is None:
                            self.current_target = self.getClosestPos(gameState, food_list)

                    # when there is ghost near by eat ghost first
                    elif len(enemy_location_list) > 0:
                        self.current_target = self.getClosestPos(gameState, enemy_location_list)
                    else:
                        pass  # eat food still
                # when the pacman  used the capsule  and no time left (avoid ghost)
                else:
                    self.return_permission = False
                    current_food_carrying = self.carrying
                    current_food_remaining = len(self.getFood(gameState).asList())

                    if self.have_target():
                        pass
                    elif current_food_remaining < 3 or current_food_carrying == MAX_CAPACITY:  # return to base
                        self.current_target = self.getClosestPos(gameState, self.boundary)
                        self.return_permission = True
                    else:
                        closest_foodloc = self.getClosestPos(gameState, food_list)
                        distance_to_food = self.getMazeDistance(self_location, closest_foodloc)
                        if len(capsules) > 0:
                            closest_capsuleloc = self.getClosestPos(gameState, capsules)
                            distance_to_capsule = self.getMazeDistance(self_location, closest_capsuleloc)
                            if distance_to_capsule <= distance_to_food:
                                self.current_target = closest_capsuleloc
                            else:

                                self.current_target = closest_foodloc


                        else:
                            self.current_target = closest_foodloc

                problem = PositionSearchProblem(gameState, self.current_target, self.index, enemy_location_list)
        else:  # when the number of eaten food have reach the goal go back to home and avoid the defence
            self.current_target = self.getClosestPos(gameState, self.boundary)
            self.return_permission = True
            enemy_location_list = self.get_enemyloc_list(gameState, enemy_index)
            problem = PositionSearchProblem(gameState, self.current_target, self.index, enemy_location_list)

        # the path finding logic(line 266 to line 284) is same as the sample/baselineTeam line 110 to line 124
        # author: University of Melbourne COMP90054 staff team
        # find a path
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

    # The method getBoundary is same as the method getBoundary in sample/baselineTeam
    # author: University of Melbourne COMP90054 staff team
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

    # The method getClosestPos is same as the method getClosestPos in sample/baselineTeam
    # author: University of Melbourne COMP90054 staff team
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

    # The method  aStarSearch is same as the method aStarSearch in sample/baselineTeam
    # author: University of Melbourne COMP90054 staff team
    def aStarSearch(self, problem):
        """Search the node that has the lowest combined cost and heuristic first."""

        from util import PriorityQueue
        myPQ = util.PriorityQueue()
        startState = problem.getStartState()

        startNode = (startState, '', 0, [])
        heuristic = problem._manhattanDistance
        myPQ.push(startNode, heuristic(startState))
        visited = set()
        best_g = dict()
        while not myPQ.isEmpty():
            node = myPQ.pop()
            state, action, cost, path = node

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


class Semi_Attack_Defence_Agent(Attack_Agent):
    """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

    def registerInitialState(self, gameState):
        """
    This is a semi attack and defence agent When the number of  pacman on self field is greater than one agent are
    able to patrol and catch the enemy if the enemy location be detected.
    Otherwise, it can attack aggressively.
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
        self.attack_permission = True
        self.return_permission = False
        self.patrol_boundary_top = True

    def get_enemy_line(self, gameState):
        boundary_location = []
        height = gameState.data.layout.height
        width = gameState.data.layout.width
        for i in range(height):
            if self.red:
                j = int(width / 2)
            else:
                j = int(width / 2) - 1
            if not gameState.hasWall(j, i):
                boundary_location.append((j, i))
        return boundary_location

    def have_enemy_in_court(self, enemy_index, gameState):
        count = 0
        for enemy_id in enemy_index:
            if self.get_agent_mode(gameState, enemy_id):  # is a pacman
                count += 1
        return count

    def patrol_on_line(self, gameState, self_boundary):
        # initially goes on the top
        top_loc = self_boundary[0]
        len_list = len(self_boundary)
        bottom_loc = self_boundary[len_list - 1]
        self_index = self.index
        self_location = gameState.getAgentPosition(self_index)
        # start patrol
        if not self.have_target():
            self.current_target = top_loc
        if self.patrol_boundary_top is True:
            # the agent patrol to the boundary top
            # when the agent arrive the top change direction of patrol
            if self_location == top_loc:
                # patrol on the boundary bottom next time
                self.patrol_boundary_top = False
                self.current_target = bottom_loc
        else:  # self.patrol_boundary_top is False
            # the agent patrol to the boundary bottom
            # when the agent arrive the bottom change direction of patrol
            if self_location == bottom_loc:
                # patrol on the boundary bottom next time
                self.patrol_boundary_top = True
                self.current_target = top_loc

    def get_enemyloc_list_defence(self, gameState, enemy_index):
        enemy_location_list = []
        for enemy_id in enemy_index:
            enemy_location = gameState.getAgentState(enemy_id).getPosition()
            # pacman = true ghost = false
            enemy_mode = self.get_agent_mode(gameState, enemy_id)
            if enemy_mode and enemy_location is not None:
                exact_enemy_loc = form_enemy_location(enemy_location)
                enemy_location_list.append(exact_enemy_loc)
        return enemy_location_list

    def chooseAction(self, gameState):
        enemy_index = self.getOpponents(gameState)
        self_boundary = self.getBoundary(gameState)
        food_list = self.getFood(gameState).asList()

        ######################
        self_index = self.index
        self_location = gameState.getAgentPosition(self_index)
        capsules = self.getCapsules(gameState)  # get the list of capsules
        enemy_location_list = self.get_enemyloc_list_defence(gameState, enemy_index)

        # patrol mode
        if self.have_enemy_in_court(enemy_index, gameState) >= 1:
            if len(enemy_location_list) > 0:  # when there is enemy around -> chase it
                self.current_target = self.getClosestPos(gameState, enemy_location_list)
            elif self.have_target():
                pass
            else:  # inspect the middle line
                self.patrol_on_line(gameState, self_boundary)
            problem = PositionSearchProblem(gameState, self.current_target, self.index)

        else:  # when there is no enemy in filed-> attack
            current_food_remaining = len(food_list)
            if current_food_remaining > 2 and self.current_target is None:  # attack and eat food
                enemy_location_list = self.get_enemyloc_list(gameState, enemy_index)
                pro_time = self.get_minimum_pro_time(gameState, enemy_index)
                current_target = self.current_target
                current_target_is_food = current_target in food_list
                # when the pacman eat the capsule
                if pro_time >= 2:
                    current_food_remaining = len(food_list)
                    if not current_target_is_food or current_target is None:
                        if len(enemy_location_list) > 0:
                            self.current_target = self.getClosestPos(gameState, enemy_location_list)
                        elif current_food_remaining > 2 and self.current_target is None:
                            self.current_target = self.getClosestPos(gameState, food_list)
                    # when there is ghost near by eat ghost first
                    elif len(enemy_location_list) > 0:
                        self.current_target = self.getClosestPos(gameState, enemy_location_list)
                    else:
                        pass  # eat food still
                # when the pacman  used the capsule and no time left (avoid ghost)
                else:
                    self.return_permission = False
                    current_food_carrying = self.carrying
                    current_food_remaining = len(self.getFood(gameState).asList())

                    if self.have_target():
                        pass
                    elif current_food_remaining < 3 or current_food_carrying == MAX_CAPACITY:  # return to base
                        self.current_target = self.getClosestPos(gameState, self.boundary)
                        self.return_permission = True
                    else:
                        closest_foodloc = self.getClosestPos(gameState, food_list)
                        distance_to_food = self.getMazeDistance(self_location, closest_foodloc)

                        if len(capsules) > 0:
                            closest_capsuleloc = self.getClosestPos(gameState, capsules)
                            distance_to_capsule = self.getMazeDistance(self_location, closest_capsuleloc)
                            if distance_to_capsule <= distance_to_food:
                                self.current_target = closest_capsuleloc
                            else:
                                self.current_target = closest_foodloc

                        else:
                            self.current_target = closest_foodloc
                problem = PositionSearchProblem(gameState, self.current_target, self.index, enemy_location_list)

            else:  # when the number of food be eaten has reach the goal -> go back and defense
                if len(enemy_location_list) > 0:  # when there is enemy -> chase
                    self.current_target = self.getClosestPos(gameState, enemy_location_list)
                elif self.have_target():
                    pass
                else:  # inspect the middle line
                    self.patrol_on_line(gameState, self_boundary)
                problem = PositionSearchProblem(gameState, self.current_target, self.index)

        # the path finding logic(line 527 to line 542) is same as the sample/baselineTeam line 110 to line 124
        # author: University of Melbourne COMP90054 staff team
        # find a path
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


# the PositionSearchProblem class is same as the PositionSearchProblem class in sample/baselineTeam
# author: University of Melbourne COMP90054 staff team
class PositionSearchProblem:
    """
    It is the ancestor class for all the search problem class.
    A search problem defines the state space, start state, goal test, successor
    function and cost function.  This search problem can be used to find paths
    to a particular point.
    """

    # the difference between the initial function with baseline team is: the wall is added in the position of
    # enemies
    def __init__(self, gameState, goal, agentIndex=0, enemy_position_list=[], costFn=lambda x: 1):
        if enemy_position_list is None:
            enemy_position_list = []
        self.walls = gameState.getWalls().copy()

        ## 测试删除枪逻辑
        for (x_loc, y_loc) in enemy_position_list:
            self.walls[x_loc][y_loc] = True
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
